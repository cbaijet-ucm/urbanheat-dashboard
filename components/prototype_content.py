"""Contenidos de prueba, cargados sólo al entrar en su subsección."""

from __future__ import annotations

import base64
import bisect
import json
from pathlib import Path

import folium
from folium.plugins import MarkerCluster
import pyarrow as pa
import pyarrow.parquet as pq
import streamlit as st
import streamlit.components.v1 as components

from data.content_store import PORT as CONTENT_STORE_PORT
from data.content_store import load_canvas_record


ASSETS = Path(__file__).resolve().parents[1] / "assets"


def render_object_canvas_editor(storage_suffix: str = "scope") -> None:
    """Editor visual basado en objetos, no en flujo de documento."""
    canvas_record = load_canvas_record(storage_suffix)
    initial_objects = canvas_record["objects"] if canvas_record else None
    initial_revision = int(canvas_record.get("revision", 0)) if canvas_record else 0
    initial_objects_json = json.dumps(initial_objects, ensure_ascii=False).replace("</", "<\\/")
    editor_html = """
        <style>
          html,body{margin:0;background:#fff;color:#161616;font-family:Arial,sans-serif;overflow:hidden}
          *{box-sizing:border-box}
          .object-editor{width:100%;border:1px solid #d5d5d5;background:#fff}
          .toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:4px;padding:5px;background:#ededed;border-bottom:1px solid #aaa}
          .toolbar .group{display:inline-flex;align-items:center;gap:3px;padding-right:6px;border-right:1px solid #bbb}
          .toolbar button,.toolbar select,.toolbar input{height:26px;border:1px solid #aaa;background:#fff;color:#111;font:12px Arial,sans-serif}
          .toolbar button{min-width:27px;padding:0 7px;cursor:pointer}
          .toolbar button:hover{border-color:#0000ff;color:#0000ff}
          .toolbar select{min-width:145px;padding:0 4px}.toolbar #font-size{width:70px;min-width:70px}.toolbar #font-size-custom{width:58px;padding:0 4px}.toolbar #line-height{width:72px;min-width:72px}.toolbar input[type=color]{width:30px;padding:1px}.toolbar #image-opacity{width:105px}.toolbar #image-opacity-value{width:52px;padding:0 4px}.toolbar #appear-step,.toolbar #disappear-step{width:45px;padding:0 3px}.toolbar #appear-duration,.toolbar #disappear-duration{width:58px;padding:0 3px}
          .canvas{position:relative;width:100%;height:1400px;overflow:hidden;background:#fff}
          .canvas-object{position:absolute;min-width:80px;min-height:42px;border:1px solid transparent;background:transparent}
          .canvas-object.selected{outline:2px solid #0000ff;outline-offset:1px}
          .object-handle{position:absolute;left:-1px;top:-22px;height:21px;min-width:28px;border:1px solid #888;background:#fff;color:#111;cursor:move;z-index:20;font:12px/18px Arial}
          .object-handle-center{left:50%;top:50%;transform:translate(-50%,-50%);width:34px;height:34px;min-width:34px;border-radius:50%;font:16px/30px Arial;opacity:.22;background:rgba(255,255,255,.82)}
          .canvas-object:hover .object-handle-center,.canvas-object.selected .object-handle-center{opacity:.9;border-color:#0000ff;color:#0000ff}
          .object-resize{position:absolute;right:-2px;bottom:-2px;width:18px;height:18px;cursor:nwse-resize;z-index:20;background:linear-gradient(135deg,transparent 0 45%,#666 46% 52%,transparent 53% 64%,#666 65% 71%,transparent 72%)}
          .text-content{width:100%;height:100%;padding:8px;overflow:auto;outline:none;line-height:1.45;white-space:normal}
          .text-content ul,.text-content ol{margin:.35em 0;padding-left:1.6em}
          .text-content table{border-collapse:collapse;min-width:60px;table-layout:auto}
          .text-content td,.text-content th{min-width:28px;padding:4px 6px;vertical-align:top}
          .text-content table[data-urbanheat-valign="top"] td,.text-content table[data-urbanheat-valign="top"] th{vertical-align:top!important}
          .text-content table[data-urbanheat-valign="middle"] td,.text-content table[data-urbanheat-valign="middle"] th{vertical-align:middle!important}
          .text-content table[data-urbanheat-valign="bottom"] td,.text-content table[data-urbanheat-valign="bottom"] th{vertical-align:bottom!important}
          .text-content table[data-urbanheat-valign] td>p,.text-content table[data-urbanheat-valign] th>p{margin-top:0!important;margin-bottom:0!important}
          .image-content{width:100%;height:100%;display:block;object-fit:contain;pointer-events:none;user-select:none}
          .arrow-content{width:100%;height:100%;display:block;overflow:visible;pointer-events:none;user-select:none}
          .web-content{width:100%;height:100%;display:block;border:0;background:#fff}
          .storage-status{margin-left:auto;padding:0 7px;color:#555;font:11px Arial,sans-serif;white-space:nowrap}.storage-status.error{color:#b00020}
          body.urbanheat-render-mode .object-editor{border:0}
          body.urbanheat-render-mode .canvas-object{border:0!important;outline:0!important}
          body.urbanheat-render-mode .toolbar,
          body.urbanheat-render-mode .object-handle,
          body.urbanheat-render-mode .object-resize,
          body.urbanheat-render-mode .storage-status{display:none!important}
        </style>
        <div class="object-editor">
          <div class="toolbar">
            <span class="group"><button id="add-text">Insertar cuadro de texto</button><button id="add-image">Insertar imagen</button><input id="image-file" type="file" accept="image/*" hidden></span>
            <span class="group"><select id="font">
              <option>Arial</option><option>Helvetica</option><option>Inter</option><option>Roboto</option><option>Aptos</option><option>Calibri</option><option>Segoe UI</option><option>Verdana</option><option>Tahoma</option><option>Trebuchet MS</option><option>Century Gothic</option><option>Georgia</option><option>Garamond</option><option>Palatino Linotype</option><option>Book Antiqua</option><option>Times New Roman</option><option>Courier New</option><option>Consolas</option><option>Impact</option>
            </select><button id="font-smaller" aria-label="Reducir tamaño">−</button><select id="font-size" aria-label="Tamaños predefinidos"><option value="" disabled>—</option><option>8</option><option>9</option><option>10</option><option>11</option><option>12</option><option>14</option><option>16</option><option selected>18</option><option>20</option><option>24</option><option>28</option><option>32</option><option>36</option><option>40</option><option>48</option><option>56</option><option>64</option><option>72</option><option>96</option><option>120</option><option>144</option></select><input id="font-size-custom" type="number" min="8" max="144" step="1" value="18" aria-label="Tamaño de fuente personalizado"><button id="font-larger" aria-label="Aumentar tamaño">+</button><select id="line-height" aria-label="Interlineado"><option value="0.8">0.80</option><option value="0.9">0.90</option><option value="1">1.00</option><option value="1.05">1.05</option><option value="1.1">1.10</option><option value="1.15">1.15</option><option value="1.2">1.20</option><option value="1.25">1.25</option><option value="1.3">1.30</option><option value="1.35">1.35</option><option value="1.4">1.40</option><option value="1.45" selected>1.45</option><option value="1.5">1.50</option><option value="1.6">1.60</option><option value="1.7">1.70</option><option value="1.8">1.80</option><option value="2">2.00</option><option value="2.25">2.25</option><option value="2.5">2.50</option><option value="3">3.00</option></select><input id="text-color" type="color" value="#161616" aria-label="Color del texto"><button id="pick-text-color" aria-label="Capturar color para el texto" title="Cuentagotas: aplicar al texto">◎T</button><input id="fill-color" type="color" value="#ffffff" aria-label="Color de fondo"><button id="pick-fill-color" aria-label="Capturar color para el fondo" title="Cuentagotas: aplicar al fondo">◎F</button></span>
            <span class="group"><button data-command="undo" aria-label="Deshacer">↶</button><button data-command="redo" aria-label="Rehacer">↷</button><button data-command="bold"><b>B</b></button><button data-command="italic"><i>I</i></button><button data-command="underline"><u>U</u></button><button data-command="strikeThrough"><s>S</s></button><button data-command="subscript">X₂</button><button data-command="superscript">X²</button></span>
            <span class="group"><button data-align="left">Izq.</button><button data-align="center">Centro</button><button data-align="right">Der.</button><button data-align="justify">Just.</button></span>
            <span class="group"><button data-command="insertUnorderedList">• Lista</button><button data-command="insertOrderedList">1. Lista</button><button data-command="outdent" aria-label="Reducir sangría">⇤</button><button data-command="indent" aria-label="Aumentar sangría">⇥</button><button data-command="removeFormat">Limpiar formato</button></span>
            <span class="group"><strong>Tabla</strong><button id="table-row-add">+ Fila</button><button id="table-row-delete">− Fila</button><button id="table-column-add">+ Col.</button><button id="table-column-delete">− Col.</button><button id="table-cell-fill">Color celda</button><button id="table-borders">Bordes</button><button id="table-valign-top">V arriba</button><button id="table-valign-middle">V centro</button><button id="table-valign-bottom">V abajo</button></span>
            <span class="group"><label for="image-opacity">Alpha</label><input id="image-opacity" type="range" min="0" max="100" step="1" value="100" disabled><input id="image-opacity-value" type="number" min="0" max="100" step="1" value="100" disabled><span>%</span></span>
            <span class="group"><strong>Secuencia</strong><label for="appear-step">Entra</label><input id="appear-step" type="number" min="0" max="99" step="1" value="0" title="Click en el que aparece. 0: visible desde el inicio"><label for="disappear-step">Sale</label><input id="disappear-step" type="number" min="0" max="99" step="1" value="0" title="Click en el que desaparece. 0: no desaparece"><label for="appear-duration">Tiempo entrada</label><input id="appear-duration" type="number" min="0" max="10000" step="50" value="400" title="Duración del fundido de entrada en milisegundos"><label for="disappear-duration">Tiempo salida</label><input id="disappear-duration" type="number" min="0" max="10000" step="50" value="400" title="Duración del fundido de salida en milisegundos"><span>ms</span><button id="sequence-reset">Reiniciar</button></span>
            <span class="group"><button id="fit-image">Ajustar a imagen</button><button id="add-background">Poner fondo</button><button id="remove-background">Quitar fondo</button></span>
            <span class="group"><button id="bring-front">Traer al frente</button><button id="send-back">Enviar al fondo</button></span>
            <span class="group"><button id="duplicate">Duplicar</button><button id="delete">Eliminar</button></span>
            <span id="storage-status" class="storage-status">Preparando guardadoâ€¦</span>
          </div>
          <div id="canvas" class="canvas"></div>
        </div>
        <script>
          const canvas=document.getElementById('canvas');
          const storageKey='urbanheat-' + __STORAGE_SUFFIX__ + '-object-canvas-v1';
          const canvasKey=__STORAGE_SUFFIX__;
          const storeUrl='http://127.0.0.1:__CONTENT_STORE_PORT__/canvas/'+encodeURIComponent(canvasKey);
          const initialObjects=__INITIAL_OBJECTS__;
          let objects=Array.isArray(initialObjects)?initialObjects:[];
          let selectedId=null; const selectedIds=new Set(); let sequence=0; let savedTextRange=null; let activeTableCell=null; let applySequence=()=>{};
          let sequenceStep=0;
          let revision=__INITIAL_REVISION__; let pendingRevision=revision; let saveTimer=null; let pendingSnapshot=null;
          let saveChain=Promise.resolve();
          let isRenderMode=false;
          const syncRenderMode=()=>{
            try{
              const parentDocument=window.parent && window.parent.document;
              const isRender=parentDocument && parentDocument.documentElement.dataset.urbanheatMode==='render';
              const nextRenderMode=!!isRender;
              if(nextRenderMode!==isRenderMode)sequenceStep=0;
              isRenderMode=nextRenderMode;
              document.body.classList.toggle('urbanheat-render-mode',!!isRender);
              applySequence();
              document.querySelectorAll('.text-content').forEach(content=>{
                content.contentEditable=String(!isRenderMode);
                content.setAttribute('aria-readonly',String(isRenderMode));
                content.style.cursor=isRenderMode?'default':'text';
              });
            }catch(_){ }
          };
          syncRenderMode();
          try{
            const parentDocument=window.parent && window.parent.document;
            if(parentDocument){
              new MutationObserver(syncRenderMode).observe(parentDocument.documentElement,{attributes:true,attributeFilter:['data-urbanheat-mode']});
            }
          }catch(_){ }
          const storageStatus=document.getElementById('storage-status');
          const setStorageStatus=(message,isError=false)=>{storageStatus.textContent=message;storageStatus.classList.toggle('error',isError)};
          const fontSizes=[8,9,10,11,12,14,16,18,20,24,28,32,36,40,48,56,64,72,96,120,144];
          const uid=()=>`object-${Date.now()}-${++sequence}`;
          const baseStyle=()=>({fontFamily:'Arial',fontSize:18,lineHeight:'1.45',color:'#161616',background:'#ffffff',textAlign:'left',fontWeight:'normal',fontStyle:'normal',textDecoration:'none'});
          if(!objects.length)objects=[{id:uid(),type:'text',x:30,y:35,w:520,h:110,html:'Escribe aquí el contenido.',style:baseStyle()}];
          const persistSnapshot=(snapshot,snapshotRevision)=>{
            saveChain=saveChain.catch(()=>{}).then(async()=>{
              const response=await fetch(storeUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({revision:snapshotRevision,objects:snapshot})});
              const result=await response.json().catch(()=>({}));
              if(!response.ok)throw new Error(result.error||`HTTP ${response.status}`);
              if(snapshotRevision===pendingRevision)setStorageStatus('Guardado en disco');
            }).catch(error=>{setStorageStatus('Error de guardado',true);console.error('No se pudo guardar el lienzo en disco',error)});
          };
          const flushSave=()=>{
            window.clearTimeout(saveTimer);
            if(!pendingSnapshot)return;
            const snapshot=pendingSnapshot;
            const snapshotRevision=pendingRevision;
            persistSnapshot(snapshot,snapshotRevision);
          };
          const save=(immediate=false)=>{
            pendingSnapshot=JSON.parse(JSON.stringify(objects));
            pendingRevision=++revision;
            setStorageStatus('Guardando en discoâ€¦');
            window.clearTimeout(saveTimer);
            if(immediate)flushSave();
            else saveTimer=window.setTimeout(flushSave,300);
            return true;
          };
          const selected=()=>objects.find(item=>item.id===selectedId);
          const captureTextRange=content=>{const selection=window.getSelection();if(!selection||!selection.rangeCount)return;const range=selection.getRangeAt(0);if(!content.contains(range.commonAncestorContainer))return;savedTextRange=range.cloneRange();let node=range.commonAncestorContainer;if(node.nodeType!==Node.ELEMENT_NODE)node=node.parentElement;const cell=node?.closest?.('td,th');if(cell&&content.contains(cell))activeTableCell=cell};
          const clamp=(value,min,max)=>Math.min(max,Math.max(min,value));
          const updateToolbar=()=>{
            const item=selected();
            const opacity=document.getElementById('image-opacity');
            const opacityValue=document.getElementById('image-opacity-value');
            const isImage=Boolean(item&&item.type==='image');
            opacity.disabled=!isImage;opacityValue.disabled=!isImage;
            document.getElementById('appear-step').value=String(item?.appearStep??0);
            document.getElementById('disappear-step').value=String(item?.disappearStep??0);
            document.getElementById('appear-duration').value=String(item?.appearDuration??400);
            document.getElementById('disappear-duration').value=String(item?.disappearDuration??400);
            document.getElementById('appear-step').disabled=!item;
            document.getElementById('disappear-step').disabled=!item;
            document.getElementById('appear-duration').disabled=!item;
            document.getElementById('disappear-duration').disabled=!item;
            document.getElementById('fit-image').disabled=!isImage;
            document.getElementById('add-background').disabled=!item||item.type!=='text';
            document.getElementById('remove-background').disabled=!item||!['text','image'].includes(item.type);
            if(isImage){const alpha=item.opacity??100;opacity.value=String(alpha);opacityValue.value=String(alpha)}
            if(!item||item.type!=='text')return;
            document.getElementById('font').value=item.style.fontFamily||'Arial';
            const size=item.style.fontSize||18;
            document.getElementById('font-size').value=fontSizes.includes(Number(size))?String(size):'';
            document.getElementById('font-size-custom').value=String(size);
            document.getElementById('line-height').value=String(item.style.lineHeight||'1.45');
            document.getElementById('text-color').value=item.style.color||'#161616';
            document.getElementById('fill-color').value=(item.style.background||'').startsWith('#')?item.style.background:'#ffffff';
          };
          const selectObject=(id,additive=false)=>{
            if(id===null){selectedIds.clear();selectedId=null}
            else if(additive){
              if(selectedIds.has(id)){selectedIds.delete(id);if(selectedId===id)selectedId=Array.from(selectedIds).at(-1)||null}
              else{selectedIds.add(id);selectedId=id}
            }else{selectedIds.clear();selectedIds.add(id);selectedId=id}
            document.querySelectorAll('.canvas-object').forEach(node=>node.classList.toggle('selected',selectedIds.has(node.dataset.id)));
            updateToolbar();
          };
          const sequenceValue=(value,maximum=99)=>clamp(parseInt(value,10)||0,0,maximum);
          const presentationControlsSequence=()=>{
            return canvasKey==='scope'&&isRenderMode;
          };
          const isVisibleAtStep=(item,step=sequenceStep)=>{
            const appearsAt=sequenceValue(item.appearStep);
            const disappearsAt=sequenceValue(item.disappearStep);
            return !isRenderMode || (step>=appearsAt && (!disappearsAt || step<disappearsAt));
          };
          const stopFade=node=>node.getAnimations?.().forEach(animation=>animation.cancel());
          const setNodeVisibility=(node,visible)=>{
            stopFade(node);
            node.style.display=visible?'block':'none';
            node.style.opacity=visible?'1':'0';
          };
          const fadeNode=(node,from,to,duration,onfinish)=>{
            stopFade(node);
            node.style.display='block';
            node.style.opacity=String(from);
            if(duration<=0){node.style.opacity=String(to);onfinish?.();return}
            const animation=node.animate([{opacity:from},{opacity:to}],{duration,easing:'ease-in-out',fill:'forwards'});
            animation.onfinish=()=>{node.style.opacity=String(to);onfinish?.()};
          };
          applySequence=(animate=false,previousStep=sequenceStep)=>objects.forEach(item=>{
            const node=document.querySelector(`.canvas-object[data-id="${item.id}"]`);
            if(!node)return;
            if(!isRenderMode){setNodeVisibility(node,true);return}
            const wasVisible=isVisibleAtStep(item,previousStep);
            const isVisible=isVisibleAtStep(item,sequenceStep);
            if(!animate||wasVisible===isVisible){setNodeVisibility(node,isVisible);return}
            if(isVisible){
              fadeNode(node,0,1,sequenceValue(item.appearDuration??400,10000));
            }else{
              fadeNode(node,1,0,sequenceValue(item.disappearDuration??400,10000),()=>{
                if(isRenderMode&&!isVisibleAtStep(item))node.style.display='none';
              });
            }
          });
          const bindGeometry=(node,item)=>{
            const handles=node.querySelectorAll('.object-handle'),resize=node.querySelector('.object-resize');
            handles.forEach(handle=>handle.addEventListener('pointerdown',event=>{
                event.preventDefault();event.stopPropagation();if(!selectedIds.has(item.id))selectObject(item.id,event.ctrlKey||event.metaKey||event.shiftKey);
                const moving=objects.filter(candidate=>selectedIds.has(candidate.id));
                const origins=new Map(moving.map(candidate=>[candidate.id,{x:candidate.x,y:candidate.y}]));
                const sx=event.clientX,sy=event.clientY;
                const minDx=Math.max(...moving.map(candidate=>-candidate.x));
                const maxDx=Math.min(...moving.map(candidate=>canvas.clientWidth-candidate.x-candidate.w));
                const minDy=Math.max(...moving.map(candidate=>-candidate.y));
                const maxDy=Math.min(...moving.map(candidate=>canvas.clientHeight-candidate.y-candidate.h));
                const move=next=>{next.preventDefault();const dx=clamp(next.clientX-sx,minDx,maxDx),dy=clamp(next.clientY-sy,minDy,maxDy);moving.forEach(candidate=>{const origin=origins.get(candidate.id);candidate.x=origin.x+dx;candidate.y=origin.y+dy;const candidateNode=document.querySelector(`.canvas-object[data-id="${candidate.id}"]`);if(candidateNode){candidateNode.style.left=candidate.x+'px';candidateNode.style.top=candidate.y+'px'}})};
                const end=()=>{document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',end,true);save()};
                document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',end,true);
              }));
            resize.addEventListener('pointerdown',event=>{
              event.preventDefault();event.stopPropagation();selectObject(item.id);
              const sx=event.clientX,sy=event.clientY,ow=item.w,oh=item.h;
              const move=next=>{next.preventDefault();item.w=clamp(ow+next.clientX-sx,80,canvas.clientWidth-item.x);item.h=clamp(oh+next.clientY-sy,42,canvas.clientHeight-item.y);node.style.width=item.w+'px';node.style.height=item.h+'px'};
              const end=()=>{document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',end,true);save()};
              document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',end,true);
            });
          };
          const bindTableResizing=(content,item)=>{
            const edgeAt=event=>{
              const cell=event.target?.closest?.('td,th');
              if(!cell||!content.contains(cell))return null;
              const rect=cell.getBoundingClientRect();
              const right=Math.abs(rect.right-event.clientX);
              const bottom=Math.abs(rect.bottom-event.clientY);
              if(right<=6&&right<=bottom)return {cell,axis:'column'};
              if(bottom<=6)return {cell,axis:'row'};
              return null;
            };
            content.addEventListener('pointermove',event=>{
              if(isRenderMode){content.style.cursor='default';return}
              if(event.buttons)return;
              const edge=edgeAt(event);
              content.style.cursor=edge?.axis==='column'?'col-resize':edge?.axis==='row'?'row-resize':'text';
            });
            content.addEventListener('pointerleave',()=>{content.style.cursor=isRenderMode?'default':'text'});
            content.addEventListener('pointerdown',event=>{
              if(isRenderMode)return;
              const edge=edgeAt(event);if(!edge)return;
              event.preventDefault();event.stopPropagation();selectObject(item.id);
              const table=edge.cell.closest('table');const row=edge.cell.parentElement;
              const startX=event.clientX,startY=event.clientY;
              const startTableWidth=table.getBoundingClientRect().width;
              const column=edge.cell.cellIndex;
              const columnCells=Array.from(table.rows).map(tableRow=>tableRow.cells[column]).filter(Boolean);
              const startColumnWidths=columnCells.map(cell=>cell.getBoundingClientRect().width);
              const startRowHeight=row.getBoundingClientRect().height;
              table.style.tableLayout='fixed';
              const move=next=>{
                next.preventDefault();
                if(edge.axis==='column'){
                  const delta=next.clientX-startX;
                  columnCells.forEach((cell,index)=>cell.style.width=Math.max(28,startColumnWidths[index]+delta)+'px');
                  table.style.width=Math.max(60,startTableWidth+delta)+'px';
                }else{
                  row.style.height=Math.max(24,startRowHeight+next.clientY-startY)+'px';
                }
              };
              const finish=()=>{
                document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',finish,true);
                item.html=content.innerHTML;content.style.cursor='text';save();setStorageStatus('Dimensiones de tabla guardadas');
              };
              document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',finish,true);
            },true);
          };
          const render=()=>{
            canvas.innerHTML='';
            objects.forEach(item=>{
              const node=document.createElement('div');node.className='canvas-object';node.dataset.id=item.id;
              Object.assign(node.style,{left:item.x+'px',top:item.y+'px',width:item.w+'px',height:item.h+'px'});
              node.style.display=isVisibleAtStep(item)?'block':'none';
              const handle=document.createElement('button');handle.className='object-handle';handle.textContent='✥';handle.setAttribute('aria-label','Mover objeto');
              const centerHandle=document.createElement('button');centerHandle.className='object-handle object-handle-center';centerHandle.textContent='✥';centerHandle.setAttribute('aria-label','Mover objeto desde el centro');
              const resize=document.createElement('span');resize.className='object-resize';
              node.append(handle);
              if(item.type==='text'){
                const content=document.createElement('div');content.className='text-content';content.contentEditable=String(!isRenderMode);content.setAttribute('aria-readonly',String(isRenderMode));content.innerHTML=item.html||'';
                Object.assign(content.style,item.style||baseStyle());content.style.fontSize=((item.style&&item.style.fontSize)||18)+'px';
                content.addEventListener('input',()=>{if(isRenderMode)return;item.html=content.innerHTML;save()});
                content.addEventListener('paste',event=>{if(isRenderMode){event.preventDefault();return}window.setTimeout(()=>{item.html=content.innerHTML;save()},0)});
                content.addEventListener('keydown',event=>{if(isRenderMode){if(event.key.length===1||event.key==='Backspace'||event.key==='Delete'||event.key==='Enter')event.preventDefault();return}if(!(event.ctrlKey||event.metaKey))return;const key=event.key.toLowerCase();if(key==='z'){event.preventDefault();document.execCommand(event.shiftKey?'redo':'undo',false,null);item.html=content.innerHTML;save()}else if(key==='y'){event.preventDefault();document.execCommand('redo',false,null);item.html=content.innerHTML;save()}});
                content.addEventListener('focus',()=>{if(!selectedIds.has(item.id))selectObject(item.id)});
                content.addEventListener('pointerdown',event=>{const cell=event.target?.closest?.('td,th');if(cell&&content.contains(cell))activeTableCell=cell});
                content.addEventListener('mouseup',()=>captureTextRange(content));
                content.addEventListener('keyup',()=>captureTextRange(content));
                bindTableResizing(content,item);
                node.append(content);
              }else if(item.type==='image'){
                const image=document.createElement('img');image.className='image-content';image.src=item.src;image.style.opacity=String((item.opacity??100)/100);node.append(image);
              }else if(item.type==='arrow'){
                const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.classList.add('arrow-content');svg.setAttribute('viewBox','0 0 100 100');svg.setAttribute('preserveAspectRatio','none');
                const markerId='arrowhead-'+String(item.id).replace(/[^a-zA-Z0-9_-]/g,'');
                const defs=document.createElementNS('http://www.w3.org/2000/svg','defs');const marker=document.createElementNS('http://www.w3.org/2000/svg','marker');marker.setAttribute('id',markerId);marker.setAttribute('markerWidth','6');marker.setAttribute('markerHeight','6');marker.setAttribute('refX','8');marker.setAttribute('refY','5');marker.setAttribute('viewBox','0 0 10 10');marker.setAttribute('orient','auto-start-reverse');marker.setAttribute('markerUnits','strokeWidth');
                const head=document.createElementNS('http://www.w3.org/2000/svg','path');head.setAttribute('d','M 0 0 L 10 5 L 0 10 z');head.setAttribute('fill',item.stroke||'#161616');head.dataset.arrowPart='head';marker.append(head);defs.append(marker);svg.append(defs);
                const line=document.createElementNS('http://www.w3.org/2000/svg','line');line.setAttribute('x1','5');line.setAttribute('y1','50');line.setAttribute('x2','86');line.setAttribute('y2','50');line.setAttribute('stroke',item.stroke||'#161616');line.setAttribute('stroke-width',String(item.strokeWidth??4));line.setAttribute('vector-effect','non-scaling-stroke');line.setAttribute('marker-end',`url(#${markerId})`);line.dataset.arrowPart='line';svg.append(line);node.append(svg);
              }else if(item.type==='web'){
                const frame=document.createElement('iframe');frame.className='web-content';frame.src=item.src;frame.loading='lazy';frame.allow='fullscreen';frame.referrerPolicy='strict-origin-when-cross-origin';frame.setAttribute('title',item.title||'Contenido web incrustado');node.append(frame);
              }
              node.append(centerHandle);node.append(resize);node.addEventListener('pointerdown',event=>selectObject(item.id,event.ctrlKey||event.metaKey||event.shiftKey));canvas.append(node);bindGeometry(node,item);
            });
            document.querySelectorAll('.canvas-object').forEach(node=>node.classList.toggle('selected',selectedIds.has(node.dataset.id)));updateToolbar();save();
            syncRenderMode();
          };
          const selectOnly=id=>{selectedIds.clear();selectedIds.add(id);selectedId=id};
          const addText=()=>{const item={id:uid(),type:'text',x:40,y:40,w:420,h:120,html:'Nuevo texto',style:baseStyle()};objects.push(item);selectOnly(item.id);render()};
          const imageDimensions=(naturalWidth,naturalHeight,maxWidth=null)=>{const aspect=Math.max(.01,naturalWidth/naturalHeight);let width=Math.min(maxWidth||760,Math.max(240,canvas.clientWidth-100));let height=width/aspect;const maxHeight=700;if(height>maxHeight){height=maxHeight;width=height*aspect}return {w:Math.max(80,Math.round(width)),h:Math.max(42,Math.round(height))}};
          document.getElementById('add-text').onclick=addText;
          document.getElementById('add-image').onclick=()=>document.getElementById('image-file').click();
          document.getElementById('image-file').onchange=event=>{const file=event.target.files[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{const probe=new Image();probe.onload=()=>{const size=imageDimensions(probe.naturalWidth,probe.naturalHeight);const item={id:uid(),type:'image',x:50,y:80,w:size.w,h:size.h,src:reader.result,opacity:100};objects.push(item);selectOnly(item.id);render();save(true)};probe.src=reader.result};reader.readAsDataURL(file);event.target.value=''};
          document.getElementById('fit-image').onclick=()=>{const item=selected();if(!item||item.type!=='image')return;const probe=new Image();probe.onload=()=>{const size=imageDimensions(probe.naturalWidth,probe.naturalHeight,item.w);item.w=size.w;item.h=size.h;render()};probe.src=item.src};
          const applyImageOpacity=value=>{const item=selected();if(!item||item.type!=='image')return;const alpha=clamp(parseInt(value,10)||0,0,100);item.opacity=alpha;document.getElementById('image-opacity').value=String(alpha);document.getElementById('image-opacity-value').value=String(alpha);const image=document.querySelector(`.canvas-object[data-id="${item.id}"] .image-content`);if(image)image.style.opacity=String(alpha/100);save()};
          document.getElementById('image-opacity').oninput=event=>applyImageOpacity(event.target.value);
          document.getElementById('image-opacity-value').oninput=event=>applyImageOpacity(event.target.value);
          const setSequenceStep=(property,value)=>{const item=selected();if(!item)return;item[property]=sequenceValue(value);save();applySequence()};
          const setSequenceDuration=(property,value)=>{const item=selected();if(!item)return;item[property]=sequenceValue(value,10000);save();applySequence()};
          document.getElementById('appear-step').oninput=event=>setSequenceStep('appearStep',event.target.value);
          document.getElementById('disappear-step').oninput=event=>setSequenceStep('disappearStep',event.target.value);
          document.getElementById('appear-duration').oninput=event=>setSequenceDuration('appearDuration',event.target.value);
          document.getElementById('disappear-duration').oninput=event=>setSequenceDuration('disappearDuration',event.target.value);
          document.getElementById('sequence-reset').onclick=()=>{sequenceStep=0;applySequence();setStorageStatus('Secuencia reiniciada')};
          document.getElementById('add-background').onclick=()=>{const item=selected();if(!item||item.type!=='text')return;applyTextStyle({background:document.getElementById('fill-color').value||'#ffffff'})};
          const removeBackground=()=>{const item=selected();if(!item||item.type==='web')return;if(item.type==='text'){applyTextStyle({background:'transparent'});return}const source=new Image();source.onload=()=>{const work=document.createElement('canvas');work.width=source.naturalWidth;work.height=source.naturalHeight;const context=work.getContext('2d',{willReadFrequently:true});context.drawImage(source,0,0);const pixels=context.getImageData(0,0,work.width,work.height);const data=pixels.data;const corners=[0,(work.width-1)*4,(work.width*(work.height-1))*4,(work.width*work.height-1)*4];const background=corners.reduce((rgb,index)=>[rgb[0]+data[index],rgb[1]+data[index+1],rgb[2]+data[index+2]],[0,0,0]).map(value=>value/corners.length);for(let index=0;index<data.length;index+=4){const distance=Math.hypot(data[index]-background[0],data[index+1]-background[1],data[index+2]-background[2]);if(distance<=22)data[index+3]=0;else if(distance<58)data[index+3]=Math.round(data[index+3]*(distance-22)/36)}context.putImageData(pixels,0,0);item.src=work.toDataURL('image/png');render()};source.src=item.src};
          document.getElementById('remove-background').onclick=removeBackground;
          const applyTextStyle=(patch)=>{const item=selected();if(!item||item.type!=='text')return;Object.assign(item.style,patch);const content=document.querySelector(`.canvas-object[data-id="${item.id}"] .text-content`);if(!content)return;Object.assign(content.style,patch);if(patch.fontSize!==undefined)content.style.fontSize=patch.fontSize+'px';save()};
          const formatProperties={fontFamily:'font-family',fontSize:'font-size',lineHeight:'line-height',color:'color'};
          const setFormatStyle=(node,patch)=>Object.entries(patch).forEach(([property,value])=>{
            const cssProperty=formatProperties[property];if(!cssProperty)return;
            const cssValue=property==='fontSize'?Number(value)+'px':String(value);
            node.style.setProperty(cssProperty,cssValue,'important');
            if(property==='fontFamily')node.removeAttribute('face');
            if(property==='fontSize')node.removeAttribute('size');
            if(property==='color')node.removeAttribute('color');
          });
          const applyFormatToTree=(root,patch)=>{
            const nodes=[];if(root instanceof HTMLElement)nodes.push(root);
            if(root.querySelectorAll)nodes.push(...root.querySelectorAll('*'));
            nodes.forEach(node=>{if(node instanceof HTMLElement)setFormatStyle(node,patch)});
          };
          const applyTextFormat=(patch)=>{
            const item=selected();if(!item||item.type!=='text')return;
            const content=document.querySelector(`.canvas-object[data-id="${item.id}"] .text-content`);if(!content)return;
            const hasRange=savedTextRange&&content.contains(savedTextRange.commonAncestorContainer)&&!savedTextRange.collapsed;
            if(!hasRange){
              Object.assign(item.style,patch);applyFormatToTree(content,patch);
              item.html=content.innerHTML;save();return;
            }
            const range=savedTextRange.cloneRange();const fragment=range.extractContents();applyFormatToTree(fragment,patch);
            const span=document.createElement('span');setFormatStyle(span,patch);span.appendChild(fragment);range.insertNode(span);
            const selection=window.getSelection();const formattedRange=document.createRange();formattedRange.selectNodeContents(span);selection.removeAllRanges();selection.addRange(formattedRange);savedTextRange=formattedRange.cloneRange();
            item.html=content.innerHTML;save();setStorageStatus('Formato aplicado');
          };
          document.getElementById('font').onchange=event=>applyTextFormat({fontFamily:event.target.value});
          document.getElementById('font-size').onchange=event=>{const value=Number(event.target.value);document.getElementById('font-size-custom').value=String(value);applyTextFormat({fontSize:value})};
          document.getElementById('font-size-custom').oninput=event=>{const value=clamp(parseInt(event.target.value,10)||8,8,144);document.getElementById('font-size').value=fontSizes.includes(value)?String(value):'';applyTextFormat({fontSize:value})};
          document.getElementById('line-height').onchange=event=>applyTextFormat({lineHeight:event.target.value});
          const nudgeFontSize=delta=>{const item=selected();if(!item||item.type!=='text')return;const current=parseInt(document.getElementById('font-size-custom').value,10)||parseInt(item.style.fontSize,10)||18;let index=fontSizes.findIndex(size=>size>=current);if(index<0)index=fontSizes.length-1;index=clamp(index+delta,0,fontSizes.length-1);const value=fontSizes[index];document.getElementById('font-size').value=String(value);document.getElementById('font-size-custom').value=String(value);applyTextFormat({fontSize:value})};
          document.getElementById('font-smaller').onclick=()=>nudgeFontSize(-1);
          document.getElementById('font-larger').onclick=()=>nudgeFontSize(1);
          const applyTextColor=color=>applyTextFormat({color});
          document.getElementById('text-color').oninput=event=>applyTextColor(event.target.value);
          document.getElementById('fill-color').oninput=event=>applyTextStyle({background:event.target.value});
          const captureColor=async(target,apply)=>{
            if(!window.EyeDropper){target.click();setStorageStatus('Cuentagotas no disponible; usa el selector manual');return}
            try{
              const result=await new EyeDropper().open();
              target.value=result.sRGBHex;
              apply(result.sRGBHex);
              setStorageStatus(`Color ${result.sRGBHex} aplicado`);
            }catch(error){
              if(error?.name!=='AbortError')setStorageStatus('No se pudo capturar el color',true);
            }
          };
          const textPicker=document.getElementById('pick-text-color');
          const fillPicker=document.getElementById('pick-fill-color');
          textPicker.onpointerdown=event=>event.preventDefault();
          fillPicker.onpointerdown=event=>event.preventDefault();
          textPicker.onclick=()=>captureColor(document.getElementById('text-color'),applyTextColor);
          fillPicker.onclick=()=>captureColor(document.getElementById('fill-color'),color=>applyTextStyle({background:color}));
          const activeTableContext=()=>{
            const item=selected();
            if(!item||item.type!=='text')return null;
            const content=document.querySelector(`.canvas-object[data-id="${item.id}"] .text-content`);
            if(!content)return null;
            let cell=activeTableCell&&activeTableCell.isConnected&&content.contains(activeTableCell)?activeTableCell:null;
            if(!cell&&savedTextRange&&content.contains(savedTextRange.commonAncestorContainer)){
              let node=savedTextRange.commonAncestorContainer;
              if(node.nodeType!==Node.ELEMENT_NODE)node=node.parentElement;
              cell=node?.closest?.('td,th');
            }
            if(!cell||!content.contains(cell))return null;
            return {item,content,cell,row:cell.parentElement,table:cell.closest('table')};
          };
          const focusCell=cell=>{
            const range=document.createRange();range.selectNodeContents(cell);range.collapse(true);
            const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);
            savedTextRange=range.cloneRange();activeTableCell=cell;cell.closest('.text-content')?.focus();
          };
          const commitTable=(context,focusTarget=context.cell)=>{
            context.item.html=context.content.innerHTML;
            if(focusTarget&&focusTarget.isConnected)focusCell(focusTarget);
            save();setStorageStatus('Tabla actualizada');
          };
          const withTableCell=operation=>{
            const context=activeTableContext();
            if(!context){setStorageStatus('Sitúa el cursor dentro de una celda',true);return}
            operation(context);
          };
          document.querySelectorAll('#table-row-add,#table-row-delete,#table-column-add,#table-column-delete,#table-cell-fill,#table-borders,#table-valign-top,#table-valign-middle,#table-valign-bottom').forEach(button=>button.onpointerdown=event=>event.preventDefault());
          document.getElementById('table-row-add').onclick=()=>withTableCell(context=>{
            const newRow=document.createElement('tr');
            Array.from(context.row.cells).forEach(source=>{const cell=document.createElement(source.tagName.toLowerCase());cell.innerHTML='<br>';if(source.style.cssText)cell.style.cssText=source.style.cssText;newRow.append(cell)});
            context.row.after(newRow);commitTable(context,newRow.cells[Math.min(context.cell.cellIndex,newRow.cells.length-1)]);
          });
          document.getElementById('table-row-delete').onclick=()=>withTableCell(context=>{
            const rows=Array.from(context.table.rows);const index=rows.indexOf(context.row);
            if(rows.length===1){context.table.remove();context.item.html=context.content.innerHTML;save();setStorageStatus('Tabla eliminada');return}
            const next=rows[index+1]||rows[index-1];context.row.remove();commitTable(context,next.cells[Math.min(context.cell.cellIndex,next.cells.length-1)]);
          });
          document.getElementById('table-column-add').onclick=()=>withTableCell(context=>{
            const column=context.cell.cellIndex;let target=null;
            Array.from(context.table.rows).forEach(row=>{const source=row.cells[Math.min(column,row.cells.length-1)];const cell=document.createElement((source?.tagName||'TD').toLowerCase());cell.innerHTML='<br>';if(source?.style.cssText)cell.style.cssText=source.style.cssText;if(source)source.after(cell);else row.append(cell);if(row===context.row)target=cell});
            commitTable(context,target);
          });
          document.getElementById('table-column-delete').onclick=()=>withTableCell(context=>{
            const column=context.cell.cellIndex;
            if(Array.from(context.table.rows).every(row=>row.cells.length<=1)){context.table.remove();context.item.html=context.content.innerHTML;save();setStorageStatus('Tabla eliminada');return}
            let target=null;Array.from(context.table.rows).forEach(row=>{const cell=row.cells[column];if(cell){const candidate=row.cells[column+1]||row.cells[column-1];if(row===context.row)target=candidate;cell.remove()}});commitTable(context,target);
          });
          document.getElementById('table-cell-fill').onclick=()=>withTableCell(context=>{context.cell.style.backgroundColor=document.getElementById('fill-color').value;commitTable(context)});
          document.getElementById('table-borders').onclick=()=>withTableCell(context=>{
            const enabled=context.table.dataset.urbanheatBorders!=='on';context.table.dataset.urbanheatBorders=enabled?'on':'off';context.table.style.borderCollapse='collapse';
            context.table.querySelectorAll('td,th').forEach(cell=>cell.style.border=enabled?'1px solid #777':'none');commitTable(context);
          });
          const setTableVerticalAlignment=value=>withTableCell(context=>{
            context.table.dataset.urbanheatValign=value;
            context.table.querySelectorAll('td,th').forEach(cell=>{
              cell.style.setProperty('vertical-align',value,'important');
              cell.setAttribute('valign',value);
              Array.from(cell.children).forEach(child=>{
                if(['P','DIV'].includes(child.tagName)){
                  child.style.setProperty('margin-top','0','important');
                  child.style.setProperty('margin-bottom','0','important');
                }
              });
            });
            commitTable(context);setStorageStatus(`Alineación vertical: ${value==='middle'?'centro':value==='top'?'arriba':'abajo'}`);
          });
          document.getElementById('table-valign-top').onclick=()=>setTableVerticalAlignment('top');
          document.getElementById('table-valign-middle').onclick=()=>setTableVerticalAlignment('middle');
          document.getElementById('table-valign-bottom').onclick=()=>setTableVerticalAlignment('bottom');
          document.querySelectorAll('[data-align]').forEach(button=>button.onclick=()=>applyTextStyle({textAlign:button.dataset.align}));
          document.querySelectorAll('[data-command]').forEach(button=>button.onmousedown=event=>{event.preventDefault();const item=selected();if(!item||item.type!=='text')return;const content=document.querySelector(`.canvas-object[data-id="${item.id}"] .text-content`);content.focus();document.execCommand(button.dataset.command,false,null);item.html=content.innerHTML;save()});
          document.getElementById('bring-front').onclick=()=>{const index=objects.findIndex(item=>item.id===selectedId);if(index<0||index===objects.length-1)return;const [item]=objects.splice(index,1);objects.push(item);render()};
          document.getElementById('send-back').onclick=()=>{const index=objects.findIndex(item=>item.id===selectedId);if(index<=0)return;const [item]=objects.splice(index,1);objects.unshift(item);render()};
          document.getElementById('duplicate').onclick=()=>{const originals=objects.filter(item=>selectedIds.has(item.id));if(!originals.length)return;selectedIds.clear();originals.forEach(item=>{const copy=JSON.parse(JSON.stringify(item));copy.id=uid();copy.x+=24;copy.y+=24;objects.push(copy);selectedIds.add(copy.id);selectedId=copy.id});render()};
          document.getElementById('delete').onclick=()=>{if(!selectedIds.size)return;objects=objects.filter(item=>!selectedIds.has(item.id));selectedIds.clear();selectedId=null;render()};
          canvas.addEventListener('pointerdown',event=>{if(event.target===canvas)selectObject(null)});
          const advanceSequence=()=>{
            if(!isRenderMode)return false;
            const lastStep=Math.max(0,...objects.flatMap(item=>[Number(item.appearStep)||0,Number(item.disappearStep)||0]));
            if(sequenceStep>=lastStep)return false;
            const previousStep=sequenceStep;
            sequenceStep+=1;applySequence(true,previousStep);
            return true;
          };
          const announceSequenceReady=()=>{
            try{
              if(window.frameElement)window.frameElement.dataset.urbanheatSequenceReady=canvasKey;
              const queued=Number(window.frameElement?.dataset.urbanheatSequencePending)||0;
              if(window.frameElement)window.frameElement.dataset.urbanheatSequencePending='0';
              for(let index=0;index<queued;index+=1)advanceSequence();
              window.parent?.postMessage({type:'urbanheat-sequence-ready',canvasKey},'*');
            }catch(_){}
          };
          canvas.addEventListener('click',()=>{
            if(presentationControlsSequence())return;
            advanceSequence();
          },true);
          window.addEventListener('message',event=>{
            if(event.data?.type==='urbanheat-sequence-advance')advanceSequence();
            if(event.data?.type==='urbanheat-sequence-reset'){sequenceStep=0;applySequence()}
          });
          render();
          window.setTimeout(()=>{syncRenderMode();applySequence();announceSequenceReady()},0);
        </script>
        """
    components.html(
        editor_html
        .replace("__STORAGE_SUFFIX__", json.dumps(storage_suffix))
        .replace("__CONTENT_STORE_PORT__", str(CONTENT_STORE_PORT))
        .replace("__INITIAL_OBJECTS__", initial_objects_json)
        .replace("__INITIAL_REVISION__", str(initial_revision)),
        height=1470,
        scrolling=False,
    )


@st.cache_resource(show_spinner=False)
def _parquet(path: str) -> pq.ParquetFile:
    return pq.ParquetFile(path)


@st.cache_data(show_spinner=False)
def _parquet_info(path: str) -> tuple[list[str], list[int]]:
    parquet = _parquet(path)
    return parquet.schema_arrow.names, [parquet.metadata.row_group(i).num_rows for i in range(parquet.num_row_groups)]


@st.cache_data(show_spinner=False)
def _read_page(path: str, columns: tuple[str, ...], page: int, page_size: int) -> tuple[object, int, int]:
    parquet = _parquet(path)
    _, group_sizes = _parquet_info(path)
    offsets = [0]
    for size in group_sizes:
        offsets.append(offsets[-1] + size)
    start = page * page_size
    end = min(start + page_size, offsets[-1])
    tables = []
    current = start
    while current < end:
        group = min(bisect.bisect_right(offsets, current) - 1, len(group_sizes) - 1)
        local_start = current - offsets[group]
        take = min(end - current, group_sizes[group] - local_start)
        tables.append(parquet.read_row_group(group, columns=list(columns)).slice(local_start, take))
        current += take
    return (tables[0] if len(tables) == 1 else pa.concat_tables(tables)), start, offsets[-1]


def render_cell_scene_table() -> None:
    path = ASSETS / "summaries" / "cell_date_sample.parquet"
    if not path.exists():
        st.warning("Aún no se ha preparado la muestra del dataset celda–escena.")
        return
    names, group_sizes = _parquet_info(str(path))
    defaults = [name for name in ("cell_id", "scene_id", "date_acquired", "LST_Celsius") if name in names]
    defaults += [name for name in names if name not in defaults][:8]
    all_columns = st.checkbox("Mostrar las 56 columnas", key="cell_scene_all_columns")
    selected = names if all_columns else st.multiselect("Columnas", names, default=defaults[:12], key="cell_scene_columns")
    if not selected:
        st.info("Selecciona al menos una columna.")
        return
    controls = st.columns((1.2, 1, 5.5), vertical_alignment="bottom")
    with controls[0]:
        page_size = st.selectbox("Filas por página", (100, 250, 500), index=1, key="cell_scene_page_size")
    pages = max(1, (sum(group_sizes) + page_size - 1) // page_size)
    with controls[1]:
        page = st.number_input("Página", min_value=1, max_value=pages, value=1, step=1, key="cell_scene_page") - 1
    with controls[2]:
        st.caption(f"{len(selected)} de {len(names)} columnas · muestra local de {sum(group_sizes):,} filas · navegación por páginas con PyArrow")
    table, start, total = _read_page(str(path), tuple(selected), int(page), int(page_size))
    st.dataframe(table.to_pandas(), height=440, width="stretch", hide_index=True)
    st.caption(f"Filas de muestra {start + 1:,}–{min(start + page_size, total):,} de {total:,}.")


@st.cache_data(show_spinner=False)
def _image_data(path: str, modified_ns: int) -> str:
    """Codifica la imagen y renueva la entrada si el archivo fue sustituido."""
    return base64.b64encode(Path(path).read_bytes()).decode("ascii")


def _resizable_image_html(key: str, source: str, default_height: int, alt: str) -> str:
    """Marco visual redimensionable con el tirador nativo del navegador.

    localStorage conserva el tamaño para este navegador sin añadir controles al
    contenido. ResizeObserver ajusta además la altura del iframe de Streamlit.
    """
    return f"""
    <style>
      html, body {{ margin: 0; background: #fff; overflow: hidden; }}
      #stage-{key} {{ position: relative; width: 100%; min-height: {default_height}px; overflow: hidden; background: #fff; }}
      #{key} {{ position:absolute; left: 0; top: 0; width: 100%; height: {default_height}px; min-width: 160px; min-height: 120px;
        overflow: hidden; box-sizing: border-box; background: #fff; border:1px solid #f0f0f0; cursor: move; user-select: none; }}
      #{key} img {{ display:block; width:100%; height:100%; object-fit:contain; }}
      .resize-handle {{ position:absolute; right:0; bottom:0; width:18px; height:18px; cursor:nwse-resize; z-index:10;
        touch-action:none; background:linear-gradient(135deg, transparent 0 45%, #9d9d9d 46% 51%, transparent 52% 62%, #9d9d9d 63% 68%, transparent 69%); }}
    </style>
    <div id="stage-{key}"><div id="{key}"><img draggable="false" alt="{alt}" src="data:image/png;base64,{source}"><div class="resize-handle" aria-label="Redimensionar"></div></div></div>
    <script>
      const stage = document.getElementById('stage-{key}');
      const box = document.getElementById({key!r});
      const storageKey = 'urbanheat-content-leftlimit-v1-{key}';
      const globalLeftLimit = 120;
      const localLeftLimit = () => {{
        const frameLeft = window.frameElement ? window.frameElement.getBoundingClientRect().left : 0;
        return globalLeftLimit - frameLeft;
      }};
      if (window.frameElement) window.frameElement.style.height = ({default_height} + 4) + 'px';
      try {{
        const saved = JSON.parse(localStorage.getItem(storageKey));
            if (saved) {{
              box.style.width = saved.width;
              box.style.height = saved.height;
              box.style.left = '0px';
              box.style.top = '0px';
        }}
      }} catch (_) {{}}
      const sync = () => {{
        const left = 0;
        const top = 0;
        box.style.left = left + 'px';
        const bottom = Math.max({default_height}, top + box.offsetHeight + 12);
        stage.style.minHeight = bottom + 'px';
        localStorage.setItem(storageKey, JSON.stringify({{
          width: box.style.width || box.offsetWidth + 'px',
          height: box.style.height || box.offsetHeight + 'px',
          left: left + 'px',
          top: top + 'px'
        }}));
        if (window.frameElement) window.frameElement.style.height = (stage.offsetHeight + 2) + 'px';
      }};
      const handle = box.querySelector('.resize-handle');
      handle.addEventListener('pointerdown', (event) => {{
        event.preventDefault(); event.stopPropagation();
        const startX = event.clientX, startY = event.clientY, startW = box.offsetWidth, startH = box.offsetHeight;
        const move = (next) => {{
          next.preventDefault();
          box.style.width = Math.max(160, startW + next.clientX - startX) + 'px';
          box.style.height = Math.max(120, startH + next.clientY - startY) + 'px';
          sync();
        }};
        const finish = () => {{
          document.removeEventListener('pointermove', move, true);
          document.removeEventListener('pointerup', finish, true);
        }};
        document.addEventListener('pointermove', move, true);
        document.addEventListener('pointerup', finish, true);
      }});
      box.addEventListener('pointerdown', (event) => {{
        if (event.target !== handle) return;
        event.preventDefault(); event.stopPropagation();
        const startX = event.clientX;
        const startY = event.clientY;
        const startLeft = parseFloat(box.style.left || '0');
        const startTop = parseFloat(box.style.top || '0');
        const move = (next) => {{
          next.preventDefault();
          box.style.left = Math.max(localLeftLimit(), startLeft + next.clientX - startX) + 'px';
          box.style.top = (startTop + next.clientY - startY) + 'px';
          sync();
        }};
        const finish = () => {{
          document.removeEventListener('pointermove', move, true);
          document.removeEventListener('pointerup', finish, true);
        }};
        document.addEventListener('pointermove', move, true);
        document.addEventListener('pointerup', finish, true);
      }});
      sync();
    </script>
    """


def render_pipeline_image() -> None:
    path = ASSETS / "graphic" / "Pipeline_dashboard.png"
    if not path.exists():
        st.warning("No encuentro la imagen del pipeline en assets/graphic/Pipeline_dashboard.png.")
        return
    source = _image_data(str(path), path.stat().st_mtime_ns)
    components.html(
        _resizable_image_html("pipeline_figure", source, 560, "Pipeline del dashboard UrbanHeat BCN"),
        height=564,
        scrolling=False,
    )


def _sentinel_indices_interactive_html() -> str:
    manifest_path = ASSETS / "maps" / "sentinel_indices_manifest.json"
    maps_dir = ASSETS / "maps" / "sentinel_indices"
    logo_path = ASSETS / "graphic" / "datos_indices_sentinel.png"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    logo_source = f"data:image/png;base64,{base64.b64encode(logo_path.read_bytes()).decode('ascii')}"
    order = [
        "REFERENCE_NDVI", "REFERENCE_NDBI", "REFERENCE_MNDWI",
        "CORE_NDVI", "CORE_NDBI", "CORE_MNDWI",
    ]
    panels = []
    for key in order:
        item = manifest[key]
        encoded = base64.b64encode((maps_dir / item["image"]).read_bytes()).decode("ascii")
        panels.append({**item, "key": key, "src": f"data:image/png;base64,{encoded}"})
    panels_json = json.dumps(panels, ensure_ascii=False)
    return f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
    <style>
      html,body{{margin:0;background:#fff;overflow:hidden;font-family:Arial,sans-serif}}
      #sentinel-stage{{position:relative;width:100%;height:980px;min-width:520px;background:#fff;overflow:hidden}}
      #sentinel-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-template-rows:repeat(2,minmax(0,1fr));gap:8px;width:calc(100% - 106px);height:100%;padding:8px}}
      .sentinel-brand{{position:absolute;right:0;top:0;width:106px;height:100%;display:flex;align-items:center;justify-content:center;overflow:visible;pointer-events:none}}
      .sentinel-brand img{{display:block;width:280px;height:auto;max-width:none;transform:rotate(-90deg)}}
      .sentinel-panel{{position:relative;min-width:0;min-height:0;border:1px solid #e1e1e1;background:#fff;overflow:hidden}}
      .sentinel-map{{position:absolute;inset:0}}
      .sentinel-label{{position:absolute;left:8px;top:8px;z-index:1000;background:rgba(255,255,255,.92);padding:4px 6px;font:12px Arial;color:#111;border:1px solid #ddd;pointer-events:none}}
      .sentinel-resize{{position:absolute;right:0;bottom:0;width:20px;height:20px;z-index:2000;cursor:nwse-resize;background:linear-gradient(135deg,transparent 0 45%,#777 46% 52%,transparent 53% 64%,#777 65% 71%,transparent 72%)}}
      .leaflet-control-attribution{{font-size:8px!important}}
    </style>
    <div id="sentinel-stage"><div id="sentinel-grid"></div><div class="sentinel-brand"><img src="{logo_source}" alt="Sentinel-2"></div><div class="sentinel-resize" aria-label="Redimensionar cuadrícula"></div></div>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const stage=document.getElementById('sentinel-stage');
      const grid=document.getElementById('sentinel-grid');
      const panels={panels_json};
      const storageKey='urbanheat-sentinel-indices-grid-v1';
      const maps=[];
      const fit=()=>{{if(window.frameElement)window.frameElement.style.height=(stage.offsetHeight+4)+'px'}};
      try{{const saved=JSON.parse(localStorage.getItem(storageKey));if(saved){{stage.style.width=saved.width;stage.style.height=saved.height}}}}catch(_){{}}
      panels.forEach((panel,index)=>{{
        const wrapper=document.createElement('div');wrapper.className='sentinel-panel';
        const mapNode=document.createElement('div');mapNode.className='sentinel-map';wrapper.appendChild(mapNode);
        const label=document.createElement('div');label.className='sentinel-label';label.textContent=panel.title;wrapper.appendChild(label);
        grid.appendChild(wrapper);
        const map=L.map(mapNode,{{zoomControl:true,attributionControl:false,preferCanvas:true}});
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{
          maxZoom:16,attribution:'Tiles © Esri',opacity:0.76
        }}).addTo(map);
        L.imageOverlay(panel.src,panel.bounds,{{opacity:1,interactive:false}}).addTo(map);
        map.fitBounds(panel.bounds,{{padding:[4,4]}});maps.push(map);
      }});
      let syncing=false;
      maps.forEach(sourceMap=>sourceMap.on('moveend zoomend',()=>{{
        if(syncing)return;
        syncing=true;
        const center=sourceMap.getCenter();const zoom=sourceMap.getZoom();
        maps.forEach(targetMap=>{{if(targetMap!==sourceMap)targetMap.setView(center,zoom,{{animate:false}})}});
        window.setTimeout(()=>{{syncing=false}},50);
      }}));
      const resize=document.querySelector('.sentinel-resize');
      resize.addEventListener('pointerdown',event=>{{event.preventDefault();event.stopPropagation();
        const sx=event.clientX,sy=event.clientY,sw=stage.offsetWidth,sh=stage.offsetHeight;
        const move=next=>{{next.preventDefault();stage.style.width=Math.max(520,sw+next.clientX-sx)+'px';stage.style.height=Math.max(520,sh+next.clientY-sy)+'px';maps.forEach(map=>map.invalidateSize())}};
        const end=()=>{{document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',end,true);localStorage.setItem(storageKey,JSON.stringify({{width:stage.style.width||stage.offsetWidth+'px',height:stage.style.height||stage.offsetHeight+'px'}}));fit()}};
        document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',end,true);
      }},true);
      fit();
    </script>
    """


def render_sentinel_indices_interactive() -> None:
    manifest = ASSETS / "maps" / "sentinel_indices_manifest.json"
    if not manifest.exists():
        st.warning("Aún no se ha generado el asset interactivo de índices Sentinel-2.")
        return
    components.html(_sentinel_indices_interactive_html(), height=984, scrolling=False)


def _meteo_evolution_html() -> str:
    manifest_path = ASSETS / "maps" / "meteo_evolution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload = json.dumps(manifest, ensure_ascii=False)
    return f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
    <style>
      html,body{{margin:0;background:#fff;overflow:hidden;font-family:Arial,sans-serif;color:#161616}}
      #meteo-stage{{position:relative;width:100%;height:760px;min-width:520px;min-height:420px;overflow:hidden;border:1px solid #ececec;box-sizing:border-box;background:#f4f4f4}}
      #meteo-map{{position:absolute;inset:0}}
      .meteo-controls{{position:absolute;z-index:1000;top:10px;right:10px;width:268px;padding:10px;background:rgba(255,255,255,.94);border:1px solid #d8d8d8;box-sizing:border-box}}
      .meteo-field{{display:grid;grid-template-columns:70px 1fr;align-items:center;gap:7px;margin-bottom:7px;font-size:12px}}
      .meteo-field select{{height:28px;min-width:0;border:1px solid #b8b8b8;background:#fff;color:#161616;font-size:12px}}
      .meteo-player{{display:flex;align-items:center;gap:5px;margin-top:3px}}
      .meteo-player button{{width:30px;height:27px;border:1px solid #c8c8c8;background:#fff;cursor:pointer;color:#161616}}
      #meteo-date{{margin-left:auto;font-size:12px;color:#525252}}
      .meteo-scale{{position:absolute;z-index:1000;right:10px;bottom:18px;width:268px;padding:8px 10px;background:rgba(255,255,255,.94);border:1px solid #d8d8d8;box-sizing:border-box}}
      .meteo-gradient{{height:11px;background:linear-gradient(90deg,#30123b,#466be3,#28bbec,#32f298,#a2fc3c,#f9e721,#fb7e21,#b81619)}}
      .meteo-scale-labels{{display:flex;justify-content:space-between;margin-top:4px;font-size:11px;color:#333}}
      .meteo-resize{{position:absolute;right:0;bottom:0;width:20px;height:20px;z-index:2000;cursor:nwse-resize;touch-action:none;background:linear-gradient(135deg,transparent 0 45%,#777 46% 52%,transparent 53% 64%,#777 65% 71%,transparent 72%)}}
      .leaflet-control-attribution{{font-size:8px!important}}
    </style>
    <div id="meteo-stage">
      <div id="meteo-map"></div>
      <div class="meteo-controls">
        <label class="meteo-field"><span>Variable</span><select id="meteo-feature"></select></label>
        <label class="meteo-field"><span>Escena</span><select id="meteo-scene"></select></label>
        <div class="meteo-player"><button id="meteo-prev" aria-label="Escena anterior">‹</button><button id="meteo-play" aria-label="Reproducir">▶</button><button id="meteo-next" aria-label="Escena siguiente">›</button><span id="meteo-date"></span></div>
      </div>
      <div class="meteo-scale"><div class="meteo-gradient"></div><div class="meteo-scale-labels"><span id="meteo-min"></span><span id="meteo-unit"></span><span id="meteo-max"></span></div></div>
      <div class="meteo-resize" aria-label="Redimensionar mapa"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const data={payload};
      const stage=document.getElementById('meteo-stage');
      const featureSelect=document.getElementById('meteo-feature');
      const sceneSelect=document.getElementById('meteo-scene');
      const staticBase=window.parent.location.origin+'/app/static/';
      data.features.forEach((item,index)=>{{const option=document.createElement('option');option.value=index;option.textContent=item.id;featureSelect.appendChild(option)}});
      data.scenes.forEach((item,index)=>{{const option=document.createElement('option');option.value=index;option.textContent=item.label;sceneSelect.appendChild(option)}});
      const map=L.map('meteo-map',{{zoomControl:true,attributionControl:true,preferCanvas:true,scrollWheelZoom:true}});
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:17,attribution:'Tiles © Esri',opacity:.78}}).addTo(map);
      let overlay=null;
      let timer=null;
      const update=()=>{{
        const feature=data.features[Number(featureSelect.value)];
        const scene=data.scenes[Number(sceneSelect.value)];
        if(overlay)map.removeLayer(overlay);
        overlay=L.imageOverlay(staticBase+scene.images[feature.id],data.bounds,{{opacity:.82,interactive:false}}).addTo(map);
        document.getElementById('meteo-date').textContent=scene.label;
        document.getElementById('meteo-min').textContent=feature.limits[0].toFixed(1);
        document.getElementById('meteo-max').textContent=feature.limits[1].toFixed(1);
        document.getElementById('meteo-unit').textContent=feature.id+(feature.unit?' · '+feature.unit:'');
      }};
      const step=(delta)=>{{sceneSelect.value=(Number(sceneSelect.value)+delta+data.scenes.length)%data.scenes.length;update()}};
      featureSelect.addEventListener('change',update);sceneSelect.addEventListener('change',update);
      document.getElementById('meteo-prev').addEventListener('click',()=>step(-1));
      document.getElementById('meteo-next').addEventListener('click',()=>step(1));
      document.getElementById('meteo-play').addEventListener('click',event=>{{
        if(timer){{clearInterval(timer);timer=null;event.currentTarget.textContent='▶'}}
        else{{timer=setInterval(()=>step(1),900);event.currentTarget.textContent='❚❚'}}
      }});
      map.setView([41.3874,2.1686],12);update();
      const fit=()=>{{map.invalidateSize();if(window.frameElement)window.frameElement.style.height=(stage.offsetHeight+4)+'px'}};
      const resize=document.querySelector('.meteo-resize');
      resize.addEventListener('pointerdown',event=>{{event.preventDefault();event.stopPropagation();const sx=event.clientX,sy=event.clientY,sw=stage.offsetWidth,sh=stage.offsetHeight;
        const move=next=>{{next.preventDefault();stage.style.width=Math.max(520,sw+next.clientX-sx)+'px';stage.style.height=Math.max(420,sh+next.clientY-sy)+'px';fit()}};
        const end=()=>{{document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',end,true);localStorage.setItem('urbanheat-meteo-map-size-v1',JSON.stringify({{width:stage.style.width,height:stage.style.height}}));fit()}};
        document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',end,true);
      }},true);
      try{{const saved=JSON.parse(localStorage.getItem('urbanheat-meteo-map-size-v1'));if(saved){{stage.style.width=saved.width;stage.style.height=saved.height}}}}catch(_){{}}
      window.addEventListener('resize',fit);fit();
    </script>
    """


def render_meteo_evolution_map() -> None:
    manifest = ASSETS / "maps" / "meteo_evolution_manifest.json"
    if not manifest.exists():
        st.warning("Aún no se han generado las capas del mapa Meteo.")
        return
    components.html(_meteo_evolution_html(), height=764, scrolling=False)


def render_slide_navigation(
    deck_class: str,
    slide_class_prefix: str,
    slide_count: int,
    initial_index: int = 0,
) -> None:
    navigation_html = """
        <style>html,body{margin:0;background:transparent;overflow:hidden}button{display:block;width:58px;height:58px;border:0;background:transparent;cursor:pointer;padding:2px}svg{display:block;width:54px;height:54px}circle,path{fill:none;stroke:#000;stroke-linecap:square;stroke-linejoin:miter}circle{stroke-width:3.8}path{stroke-width:6}button:hover circle,button:hover path{stroke:#0000ff}</style>
        <button id="next-slide" aria-label="Siguiente slide"><svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="46"/><path d="M20 50H76M56 30L77 50L56 70"/></svg></button>
        <script>
          const root=window.parent.document;
          const parentWindow=window.parent;
          const deckClass=__DECK_CLASS__;
          const slideClassPrefix=__SLIDE_PREFIX__;
          const slideCount=__SLIDE_COUNT__;
          const initialIndex=__INITIAL_INDEX__;
          const host=window.frameElement.closest('.element-container') || window.frameElement.parentElement;
          const align=()=>{const header=root.querySelector('.st-key-route_header');if(header&&host)host.style.setProperty('top',(header.getBoundingClientRect().bottom+8)+'px','important')};
          let index=Math.max(0,Math.min(initialIndex,slideCount-1));
          const show=()=>{
            const deck=root.querySelector('.'+deckClass);
            if(!deck)return;
            const slides=Array.from({length:slideCount},(_,i)=>deck.querySelector('.'+slideClassPrefix+(i+1)));
            slides.forEach((slide,i)=>{if(slide)slide.style.display=i===index?'block':'none'});
            const active=slides[index];
            if(active){active.querySelectorAll('iframe').forEach(frame=>{try{frame.contentWindow.dispatchEvent(new Event('resize'))}catch(_){}})}
          };
          document.getElementById('next-slide').addEventListener('click',()=>{index=(index+1)%slideCount;show()});
          align();show();
          new MutationObserver(()=>{align();show()}).observe(root.body,{childList:true,subtree:true});
          parentWindow.addEventListener('resize',align);
        </script>
        """
    components.html(
        navigation_html
        .replace("__DECK_CLASS__", json.dumps(deck_class))
        .replace("__SLIDE_PREFIX__", json.dumps(slide_class_prefix))
        .replace("__SLIDE_COUNT__", str(slide_count))
        .replace("__INITIAL_INDEX__", str(initial_index)),
        height=58,
        scrolling=False,
    )


def render_meteo_slide_deck() -> None:
    if st.session_state.get("presentation_mode", False):
        with st.container(key="meteo_slide_deck"):
            with st.container(key="meteo_slide_1"):
                render_object_canvas_editor("meteo")
            with st.container(key="meteo_slide_2"):
                render_meteo_evolution_map()
            with st.container(key="meteo_slide_3"):
                render_object_canvas_editor("meteo_3")
        return
    """Tres slides Meteo renderizadas una a una: HTML, mapa, HTML."""
    slide_index = int(st.session_state.get("meteo_slide_index", 0)) % 3
    if slide_index == 0:
        render_object_canvas_editor("meteo")
    elif slide_index == 1:
        render_meteo_evolution_map()
    else:
        render_object_canvas_editor("meteo_3")


def render_modelizacion_metodologia_slide_deck() -> None:
    """Formulación y split: dos lienzos HTML independientes."""
    with st.container(key="modelizacion_metodologia_slide_deck"):
        with st.container(key="modelizacion_metodologia_slide_1"):
            render_object_canvas_editor("modelizacion_metodologia_formulacion")
        with st.container(key="modelizacion_metodologia_slide_2"):
            render_object_canvas_editor("modelizacion_metodologia_split")


@st.cache_data(show_spinner=False)
def _model_comparison_payload(manifest_mtime_ns: int) -> dict[str, object]:
    """Carga las capas precalculadas: la UI no ejecuta ninguna inferencia."""
    cache_dir = ASSETS / "generated" / "model_comparison"
    manifest = json.loads((cache_dir / "manifest.json").read_text(encoding="utf-8"))
    scenes = []
    for scene in manifest["scenes"]:
        scenes.append(
            {
                **scene,
                "xgboost_src": f"http://127.0.0.1:{CONTENT_STORE_PORT}/model-comparison/{scene['xgboost']}?v={manifest_mtime_ns}",
                "cnn_src": f"http://127.0.0.1:{CONTENT_STORE_PORT}/model-comparison/{scene['cnn']}?v={manifest_mtime_ns}",
            }
        )
    return {"bounds": manifest["bounds"], "scenes": scenes}


def _model_comparison_html(payload: dict[str, object]) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False)
    return f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
    <style>
      html,body{{margin:0;background:#fff;overflow:hidden;font-family:Arial,sans-serif}}
      #comparison-stage{{position:relative;width:100%;height:760px;background:#f4f4f4;border:1px solid #e7e7e7;box-sizing:border-box;overflow:hidden}}
      #comparison-map{{position:absolute;inset:0}}
      .leaflet-image-layer{{pointer-events:none}}
      .comparison-select{{position:absolute;z-index:1200;left:56px;top:12px;background:rgba(255,255,255,.95);border:1px solid #d5d5d5;padding:8px 10px;display:flex;gap:8px;align-items:center;font-size:12px}}
      .comparison-select select{{border:0;background:#fff;font:inherit;color:#161616;min-width:130px;outline:none}}
      .comparison-legend{{position:absolute;z-index:1200;right:12px;bottom:20px;background:rgba(255,255,255,.96);border:1px solid #bdbdbd;padding:10px 12px;font-size:12px;color:#252525}}
      .comparison-legend b{{font-weight:600}}
      .comparison-colormap{{width:310px;height:17px;margin-top:8px;background:linear-gradient(90deg,#30123b 0%,#466be3 18%,#28bbec 35%,#32f298 51%,#a2fc3c 66%,#f9e721 80%,#fb7e21 91%,#b81619 100%)}}
      .comparison-scale-ticks{{position:relative;width:310px;height:25px;margin-top:1px;font-size:11px;color:#161616}}
      .comparison-scale-ticks span{{position:absolute;top:7px;transform:translateX(-50%);white-space:nowrap}}
      .comparison-scale-ticks span::before{{content:'';position:absolute;left:50%;top:-7px;height:5px;border-left:1px solid #222}}
      .comparison-side-label{{position:absolute;z-index:1250;padding:9px 14px;background:rgba(255,235,77,.97);border:2px solid #111;color:#111;font-size:27px;font-weight:700;letter-spacing:-.03em;pointer-events:none;white-space:nowrap}}
      #divider{{position:absolute;z-index:1150;top:0;bottom:0;left:50%;width:18px;transform:translateX(-50%);background:transparent;pointer-events:auto;cursor:ew-resize;touch-action:none}}
      #divider::before{{content:'';position:absolute;top:0;bottom:0;left:50%;width:2px;transform:translateX(-50%);background:#111;box-shadow:0 0 0 1px rgba(255,255,255,.9)}}
      #divider::after{{content:'↔';position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:30px;height:30px;border-radius:50%;background:#fff;border:2px solid #111;color:#111;text-align:center;line-height:27px;font-size:17px;font-weight:600}}
      #swipe{{position:absolute;z-index:1100;inset:0;width:100%;height:100%;margin:0;opacity:0;pointer-events:none}}
      .comparison-resize{{position:absolute;right:0;bottom:0;z-index:1300;width:20px;height:20px;cursor:nwse-resize;touch-action:none;background:linear-gradient(135deg,transparent 0 45%,#777 46% 52%,transparent 53% 64%,#777 65% 71%,transparent 72%)}}
      .leaflet-control-attribution{{font-size:8px!important}}
    </style>
    <div id="comparison-stage">
      <div id="comparison-map"></div>
      <label class="comparison-select">Escena de test <select id="scene-select"></select></label>
      <div id="divider"></div><input id="swipe" aria-label="Comparar XGBoost y Red CNN" type="range" min="0" max="100" value="50">
      <div id="xgb-label" class="comparison-side-label">XGBoost</div><div id="cnn-label" class="comparison-side-label">Red CNN</div>
      <div class="comparison-legend"><b>Izquierda</b> · XGBoost &nbsp; <b>Derecha</b> · Red CNN<div class="comparison-colormap"></div><div id="scale-ticks" class="comparison-scale-ticks"></div></div>
      <div class="comparison-resize" aria-label="Redimensionar mapa"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const payload={payload_json};
      const stage=document.getElementById('comparison-stage');
      const storageKey='urbanheat-model-comparison-size-v1';
      try{{const saved=JSON.parse(localStorage.getItem(storageKey));if(saved){{stage.style.width=saved.width;stage.style.height=saved.height}}}}catch(_){{}}
      const map=L.map('comparison-map',{{zoomControl:true,attributionControl:false,scrollWheelZoom:true}});
      L.control.attribution({{prefix:false}}).addTo(map);
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:17,attribution:'Tiles © Esri',opacity:.78}}).addTo(map);
      const bounds=payload.bounds, geographicBounds=L.latLngBounds(bounds);
      map.fitBounds(geographicBounds,{{padding:[4,4]}});
      const select=document.getElementById('scene-select');
      const swipe=document.getElementById('swipe');
      const divider=document.getElementById('divider');
      const xgbLabel=document.getElementById('xgb-label');
      const cnnLabel=document.getElementById('cnn-label');
      const scaleTicks=document.getElementById('scale-ticks');
      let xgbLayer,cnnLayer;
      let overlayBox={{left:0,top:0,width:0,height:0}};
      payload.scenes.forEach((scene,index)=>{{const option=document.createElement('option');option.value=index;option.textContent=scene.date;select.appendChild(option)}});
      function applySwipe(){{const value=Number(swipe.value)/100;divider.style.left=(overlayBox.left+overlayBox.width*value)+'px';const xgb=xgbLayer?.getElement();const cnn=cnnLayer?.getElement();if(xgb)xgb.style.clipPath='inset(0 '+(100-value*100)+'% 0 0)';if(cnn)cnn.style.clipPath='inset(0 0 0 '+(value*100)+'%)'}}
      function alignSwipe(){{const nw=map.latLngToContainerPoint(geographicBounds.getNorthWest()),se=map.latLngToContainerPoint(geographicBounds.getSouthEast());overlayBox={{left:Math.min(nw.x,se.x),top:Math.min(nw.y,se.y),width:Math.abs(se.x-nw.x),height:Math.abs(se.y-nw.y)}};swipe.style.left=overlayBox.left+'px';swipe.style.top='0px';swipe.style.right='auto';swipe.style.bottom='auto';swipe.style.width=overlayBox.width+'px';swipe.style.height=stage.offsetHeight+'px';divider.style.top='0px';divider.style.bottom='auto';divider.style.height=stage.offsetHeight+'px';xgbLabel.style.left=(overlayBox.left-34)+'px';xgbLabel.style.top=(overlayBox.top+10)+'px';cnnLabel.style.left=(overlayBox.left+overlayBox.width+34)+'px';cnnLabel.style.top=(overlayBox.top+10)+'px';cnnLabel.style.transform='translateX(-100%)';applySwipe()}}
      function renderScale(range){{const low=Number(range[0]),high=Number(range[1]);const interior=[];for(let tick=Math.ceil(low/10)*10;tick<high;tick+=10)interior.push(tick);const ticks=[low,...interior,high];scaleTicks.innerHTML=ticks.map(tick=>`<span style="left:${{((tick-low)/(high-low))*100}}%">${{tick}}°</span>`).join('')}}
      function setScene(){{const scene=payload.scenes[Number(select.value)];if(xgbLayer)map.removeLayer(xgbLayer);if(cnnLayer)map.removeLayer(cnnLayer);cnnLayer=L.imageOverlay(scene.cnn_src,bounds,{{opacity:1,interactive:false}}).addTo(map);xgbLayer=L.imageOverlay(scene.xgboost_src,bounds,{{opacity:1,interactive:false}}).addTo(map);renderScale(scene.range_celsius);xgbLayer.once('load',alignSwipe);cnnLayer.once('load',alignSwipe)}}
      select.addEventListener('change',setScene);swipe.addEventListener('input',applySwipe);setScene();
      const setSwipeFromPointer=clientX=>{{const rect=stage.getBoundingClientRect();const localX=clientX-rect.left;const ratio=overlayBox.width>0?(localX-overlayBox.left)/overlayBox.width:.5;swipe.value=String(Math.max(0,Math.min(100,ratio*100)));applySwipe()}};
      divider.addEventListener('pointerdown',event=>{{event.preventDefault();event.stopPropagation();divider.setPointerCapture?.(event.pointerId);setSwipeFromPointer(event.clientX);
        const move=next=>{{next.preventDefault();setSwipeFromPointer(next.clientX)}};
        const end=()=>{{document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',end,true)}};
        document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',end,true);
      }},true);
      const fit=()=>{{map.invalidateSize({{pan:false}});alignSwipe();if(window.frameElement)window.frameElement.style.height=(stage.offsetHeight+4)+'px'}};
      let fittedWhileVisible=false;
      const ensureBarcelonaFit=()=>{{
        if(stage.offsetWidth<10||stage.offsetHeight<10)return;
        map.invalidateSize({{pan:false}});
        if(!fittedWhileVisible){{map.fitBounds(geographicBounds,{{padding:[24,24],animate:false}});fittedWhileVisible=true}}
        alignSwipe();
        if(window.frameElement)window.frameElement.style.height=(stage.offsetHeight+4)+'px';
      }};
      const fitAfterLayout=()=>requestAnimationFrame(()=>requestAnimationFrame(()=>fittedWhileVisible?fit():ensureBarcelonaFit()));
      map.on('move zoom resize',alignSwipe);
      const resize=stage.querySelector('.comparison-resize');
      resize.addEventListener('pointerdown',event=>{{event.preventDefault();event.stopPropagation();const sx=event.clientX,sy=event.clientY,sw=stage.offsetWidth,sh=stage.offsetHeight;
        const move=next=>{{next.preventDefault();stage.style.width=Math.max(520,sw+next.clientX-sx)+'px';stage.style.height=Math.max(420,sh+next.clientY-sy)+'px';fit()}};
        const end=()=>{{document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',end,true);localStorage.setItem(storageKey,JSON.stringify({{width:stage.style.width||stage.offsetWidth+'px',height:stage.style.height||stage.offsetHeight+'px'}}));fit()}};
        document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',end,true);
      }},true);
      window.addEventListener('resize',fitAfterLayout);fitAfterLayout();
    </script>
    """


def render_model_comparison_map() -> None:
    manifest = ASSETS / "generated" / "model_comparison" / "manifest.json"
    if not manifest.exists():
        st.warning("Aún no se han preparado las predicciones de XGBoost y Red CNN.")
        return
    payload = _model_comparison_payload(manifest.stat().st_mtime_ns)
    components.html(_model_comparison_html(payload), height=764, scrolling=False)


@st.cache_data(show_spinner=False)
def _model_error_difference_payload(manifest_mtime_ns: int) -> dict[str, object]:
    """Carga el raster compuesto de diferencia de error, ya precalculado."""
    cache_dir = ASSETS / "generated" / "model_comparison"
    manifest = json.loads((cache_dir / "manifest.json").read_text(encoding="utf-8"))
    error = manifest["error_difference"]
    return {
        "bounds": manifest["bounds"],
        "range": error["range_celsius"],
        "src": f"http://127.0.0.1:{CONTENT_STORE_PORT}/model-comparison/{error['image']}?v={manifest_mtime_ns}",
    }


def _model_error_difference_html(payload: dict[str, object]) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False)
    return f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
    <style>
      html,body{{margin:0;background:#fff;overflow:hidden;font-family:Arial,sans-serif}}
      #error-stage{{position:relative;width:100%;height:760px;background:#f4f4f4;border:1px solid #e7e7e7;box-sizing:border-box;overflow:hidden}}
      #error-map{{position:absolute;inset:0}}
      .leaflet-image-layer{{pointer-events:none}}
      .error-heading{{position:absolute;z-index:1200;left:12px;top:12px;background:rgba(255,255,255,.96);border:1px solid #c8c8c8;padding:9px 11px;color:#151515;font-size:13px;font-weight:600}}
      .error-heading small{{display:block;margin-top:3px;font-size:11px;font-weight:400;color:#4d4d4d}}
      .error-legend{{position:absolute;z-index:1200;right:12px;bottom:20px;width:348px;background:rgba(255,255,255,.96);border:1px solid #bdbdbd;padding:10px 12px;color:#202020}}
      .error-sides{{display:flex;justify-content:space-between;font-size:12px;font-weight:700}}
      .error-sides span:first-child{{color:#2166ac}} .error-sides span:last-child{{color:#b2182b}}
      .error-gradient{{height:18px;margin-top:7px;background:linear-gradient(90deg,#2166ac,#67a9cf,#d1e5f0,#f7f7f7,#fddbc7,#ef8a62,#b2182b)}}
      .error-ticks{{position:relative;height:23px;font-size:11px}}
      .error-ticks span{{position:absolute;top:7px;transform:translateX(-50%);white-space:nowrap}}
      .error-ticks span::before{{content:'';position:absolute;top:-7px;left:50%;height:5px;border-left:1px solid #333}}
      .error-resize{{position:absolute;right:0;bottom:0;z-index:1300;width:20px;height:20px;cursor:nwse-resize;touch-action:none;background:linear-gradient(135deg,transparent 0 45%,#777 46% 52%,transparent 53% 64%,#777 65% 71%,transparent 72%)}}
      .leaflet-control-attribution{{font-size:8px!important}}
    </style>
    <div id="error-stage">
      <div id="error-map"></div>
      <div class="error-heading">Diferencia de error: CNN vs XGBoost<small>|error CNN| \u2212 |error XGBoost|, agregado sobre test</small></div>
      <div class="error-legend"><div class="error-sides"><span>CNN mejor</span><span>XGBoost mejor</span></div><div class="error-gradient"></div><div id="error-ticks" class="error-ticks"></div></div>
      <div class="error-resize" aria-label="Redimensionar mapa"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const payload={payload_json};
      const stage=document.getElementById('error-stage');
      const storageKey='urbanheat-model-error-difference-size-v1';
      try{{const saved=JSON.parse(localStorage.getItem(storageKey));if(saved){{stage.style.width=saved.width;stage.style.height=saved.height}}}}catch(_){{}}
      const map=L.map('error-map',{{zoomControl:true,attributionControl:false}});
      L.control.attribution({{prefix:false}}).addTo(map);
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:17,attribution:'Tiles \u00a9 Esri',opacity:.78}}).addTo(map);
      const bounds=L.latLngBounds(payload.bounds);
      L.imageOverlay(payload.src,bounds,{{opacity:1,interactive:false}}).addTo(map);
      map.fitBounds(bounds,{{padding:[4,4]}});
      const [low,high]=payload.range, ticks=[low,0,high];
      document.getElementById('error-ticks').innerHTML=ticks.map(value=>`<span style="left:${{((value-low)/(high-low))*100}}%">${{value>0?'+':''}}${{Number(value).toFixed(2)}} \u00b0C</span>`).join('');
      const fit=()=>{{map.invalidateSize();if(window.frameElement)window.frameElement.style.height=(stage.offsetHeight+4)+'px'}};
      const resize=stage.querySelector('.error-resize');
      resize.addEventListener('pointerdown',event=>{{event.preventDefault();event.stopPropagation();const sx=event.clientX,sy=event.clientY,sw=stage.offsetWidth,sh=stage.offsetHeight;
        const move=next=>{{next.preventDefault();stage.style.width=Math.max(520,sw+next.clientX-sx)+'px';stage.style.height=Math.max(420,sh+next.clientY-sy)+'px';fit()}};
        const end=()=>{{document.removeEventListener('pointermove',move,true);document.removeEventListener('pointerup',end,true);localStorage.setItem(storageKey,JSON.stringify({{width:stage.style.width||stage.offsetWidth+'px',height:stage.style.height||stage.offsetHeight+'px'}}));fit()}};
        document.addEventListener('pointermove',move,true);document.addEventListener('pointerup',end,true);
      }},true);
      window.addEventListener('resize',fit);fit();
    </script>
    """


def render_model_error_difference_map() -> None:
    manifest = ASSETS / "generated" / "model_comparison" / "manifest.json"
    if not manifest.exists():
        st.warning("Aún no se ha preparado el mapa de diferencia de error.")
        return
    payload = _model_error_difference_payload(manifest.stat().st_mtime_ns)
    components.html(_model_error_difference_html(payload), height=764, scrolling=False)


@st.cache_data(show_spinner=False)
def _territorial_lst_payload() -> dict:
    path = ASSETS / "maps" / "lst_territorial_aggregation.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _territorial_lst_map_html() -> str:
    payload = json.dumps(_territorial_lst_payload(), ensure_ascii=False).replace("</", "<\\/")
    return f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
    <style>
      html,body{{margin:0;background:#fff;overflow:hidden;font-family:Helvetica,Arial,sans-serif;color:#161616}}
      #territorial-stage{{position:relative;width:100%;height:760px;min-width:520px;min-height:420px;overflow:hidden;background:#fff;border:1px solid #ececec;box-sizing:border-box}}
      #territorial-map{{position:absolute;inset:0}}
      .territorial-control{{position:absolute;z-index:1000;top:12px;right:12px;width:210px;padding:10px 11px;background:rgba(255,255,255,.96);border:1px solid #d7d7d7;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
      .territorial-control label{{display:block;margin-bottom:6px;color:#525252;font-size:11px;letter-spacing:.03em;text-transform:uppercase}}
      .territorial-control select{{width:100%;height:32px;border:1px solid #a8a8a8;background:#fff;color:#161616;padding:0 7px;font-size:13px}}
      .territorial-legend{{position:absolute;z-index:1000;right:12px;bottom:18px;width:210px;padding:9px 11px;background:rgba(255,255,255,.96);border:1px solid #d7d7d7;box-sizing:border-box}}
      .territorial-legend-title{{margin-bottom:6px;font-size:12px;color:#333}}
      .territorial-gradient{{height:12px;background:linear-gradient(90deg,#000004,#1b0c41,#4a0c6b,#781c6d,#a52c60,#cf4446,#ed6925,#fb9b06,#f7d13d,#fcffa4)}}
      .territorial-ticks{{display:flex;justify-content:space-between;margin-top:4px;font-size:11px;color:#525252}}
      .territorial-resize{{position:absolute;right:0;bottom:0;width:20px;height:20px;z-index:2000;cursor:nwse-resize;touch-action:none;background:linear-gradient(135deg,transparent 0 45%,#777 46% 52%,transparent 53% 64%,#777 65% 71%,transparent 72%)}}
      .leaflet-control-attribution{{font-size:8px!important}}
      .leaflet-tooltip{{border:1px solid #d7d7d7;border-radius:0;box-shadow:0 1px 4px rgba(0,0,0,.12);font:12px Helvetica,Arial,sans-serif}}
    </style>
    <div id="territorial-stage">
      <div id="territorial-map"></div>
      <div class="territorial-control"><label for="territorial-level">Nivel de agregación</label><select id="territorial-level"></select></div>
      <div class="territorial-legend"><div class="territorial-legend-title">LST media julio–agosto (°C)</div><div class="territorial-gradient"></div><div class="territorial-ticks"><span id="territorial-min"></span><span id="territorial-mid"></span><span id="territorial-max"></span></div></div>
      <div class="territorial-resize" aria-label="Redimensionar mapa"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const data={payload};
      const stage=document.getElementById('territorial-stage');
      const selector=document.getElementById('territorial-level');
      const map=L.map('territorial-map',{{zoomControl:true,attributionControl:true,preferCanvas:true,scrollWheelZoom:true}});
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:17,attribution:'Tiles © Esri',opacity:.68}}).addTo(map);
      const palette=['#000004','#1b0c41','#4a0c6b','#781c6d','#a52c60','#cf4446','#ed6925','#fb9b06','#f7d13d','#fcffa4'];
      const lo=data.limits[0],hi=data.limits[1];
      const colorFor=value=>palette[Math.max(0,Math.min(palette.length-1,Math.floor(((value-lo)/(hi-lo||1))*palette.length)))];
      const escapeHtml=value=>String(value).replace(/[&<>\"']/g,char=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}}[char]));
      data.levels.forEach((level,index)=>{{const option=document.createElement('option');option.value=index;option.textContent=level.label;option.selected=index===1;selector.appendChild(option)}});
      document.getElementById('territorial-min').textContent=lo.toFixed(1)+'°';
      document.getElementById('territorial-mid').textContent=((lo+hi)/2).toFixed(1)+'°';
      document.getElementById('territorial-max').textContent=hi.toFixed(1)+'°';
      let layer=null;
      const renderLevel=()=>{{
        const level=data.levels[Number(selector.value)];
        if(layer)map.removeLayer(layer);
        layer=L.geoJSON(level.geojson,{{
          style:feature=>({{color:'rgba(50,50,50,.55)',weight:.55,fillColor:colorFor(feature.properties.lst),fillOpacity:.78}}),
          onEachFeature:(feature,item)=>{{
            item.bindTooltip('<strong>'+escapeHtml(feature.properties.name)+'</strong><br>LST media: '+Number(feature.properties.lst).toFixed(2)+' °C',{{sticky:true}});
            item.on({{mouseover:event=>event.target.setStyle({{weight:1.8,color:'#0000ff',fillOpacity:.9}}),mouseout:event=>layer.resetStyle(event.target)}});
          }}
        }}).addTo(map);
      }};
      selector.addEventListener('change',renderLevel);
      map.fitBounds(data.bounds,{{padding:[8,8]}});renderLevel();
      const fit=()=>{{map.invalidateSize();if(window.frameElement)window.frameElement.style.height=(stage.offsetHeight+4)+'px'}};
      try{{const saved=JSON.parse(localStorage.getItem('urbanheat-territorial-lst-size-v1'));if(saved){{stage.style.width=saved.width;stage.style.height=saved.height}}}}catch(_){{}}
      const resize=document.querySelector('.territorial-resize');
      resize.addEventListener('pointerdown',event=>{{event.preventDefault();event.stopPropagation();resize.setPointerCapture?.(event.pointerId);const sx=event.clientX,sy=event.clientY,sw=stage.offsetWidth,sh=stage.offsetHeight;
        const move=next=>{{next.preventDefault();stage.style.width=Math.max(520,sw+next.clientX-sx)+'px';stage.style.height=Math.max(420,sh+next.clientY-sy)+'px';fit()}};
        const end=()=>{{window.removeEventListener('pointermove',move,true);window.removeEventListener('pointerup',end,true);localStorage.setItem('urbanheat-territorial-lst-size-v1',JSON.stringify({{width:stage.style.width,height:stage.style.height}}));fit()}};
        window.addEventListener('pointermove',move,true);window.addEventListener('pointerup',end,true);
      }},true);
      window.addEventListener('resize',fit);fit();
    </script>
    """


def render_territorial_lst_map() -> None:
    path = ASSETS / "maps" / "lst_territorial_aggregation.json"
    if not path.exists():
        st.warning("Aún no se ha preparado el mapa de agregación territorial LST.")
        return
    components.html(_territorial_lst_map_html(), height=764, scrolling=False)


@st.cache_data(show_spinner=False)
def _thermal_social_priority_payload() -> dict:
    path = ASSETS / "maps" / "thermal_social_priority.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _thermal_social_priority_map_html() -> str:
    payload = json.dumps(_thermal_social_priority_payload(), ensure_ascii=False).replace("</", "<\\/")
    return f"""
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css">
    <style>
      html,body{{margin:0;background:#fff;overflow:hidden;font-family:Helvetica,Arial,sans-serif;color:#161616}}
      #priority-stage{{position:relative;width:100%;height:760px;min-width:520px;min-height:420px;overflow:hidden;background:#fff;border:1px solid #ececec;box-sizing:border-box}}
      #priority-map{{position:absolute;inset:0}}
      .priority-controls{{position:absolute;z-index:1000;top:12px;right:12px;width:236px;padding:10px 11px;background:rgba(255,255,255,.96);border:1px solid #d7d7d7;box-shadow:0 1px 4px rgba(0,0,0,.08)}}
      .priority-control{{display:grid;grid-template-columns:1fr 68px;align-items:center;gap:8px;margin-bottom:7px;font-size:12px}}
      .priority-control select{{height:29px;border:1px solid #a8a8a8;background:#fff;color:#161616;padding:0 5px}}
      #priority-summary{{padding-top:3px;color:#525252;font-size:11px}}
      .priority-legend{{position:absolute;z-index:1000;right:12px;bottom:18px;width:504px;padding:18px 22px;background:rgba(255,255,255,.96);border:1px solid #d7d7d7;font-size:22px;box-sizing:border-box}}
      .priority-legend-title{{margin-bottom:14px;font-size:24px;color:#333}}
      .priority-item{{display:flex;align-items:center;gap:14px;margin:10px 0}}
      .priority-swatch{{width:30px;height:30px;flex:0 0 30px;border:1px solid rgba(0,0,0,.15)}}
      .priority-resize{{position:absolute;right:0;bottom:0;width:20px;height:20px;z-index:2000;cursor:nwse-resize;touch-action:none;background:linear-gradient(135deg,transparent 0 45%,#777 46% 52%,transparent 53% 64%,#777 65% 71%,transparent 72%)}}
      .leaflet-control-attribution{{font-size:8px!important}}
      .leaflet-tooltip{{border:1px solid #d7d7d7;border-radius:0;box-shadow:0 1px 4px rgba(0,0,0,.12);font:12px Helvetica,Arial,sans-serif}}
    </style>
    <div id="priority-stage">
      <div id="priority-map"></div>
      <div class="priority-controls">
        <label class="priority-control"><span>Umbral LST</span><select id="priority-lst"></select></label>
        <label class="priority-control"><span>Umbral vulnerabilidad</span><select id="priority-vulnerability"></select></label>
        <div id="priority-summary"></div>
      </div>
      <div class="priority-legend">
        <div class="priority-legend-title">Prioridad térmico-social</div>
        <div class="priority-item"><span class="priority-swatch" style="background:#d7191c"></span>Alta exposición + alta vulnerabilidad</div>
        <div class="priority-item"><span class="priority-swatch" style="background:#f4a261"></span>Alta exposición térmica</div>
        <div class="priority-item"><span class="priority-swatch" style="background:#8e63b0"></span>Alta vulnerabilidad</div>
        <div class="priority-item"><span class="priority-swatch" style="background:#d9d9d9"></span>Sin doble condición</div>
      </div>
      <div class="priority-resize" aria-label="Redimensionar mapa"></div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const data={payload};
      const stage=document.getElementById('priority-stage');
      const lstSelect=document.getElementById('priority-lst');
      const vulnerabilitySelect=document.getElementById('priority-vulnerability');
      [lstSelect,vulnerabilitySelect].forEach(select=>{{for(let decile=1;decile<=10;decile++){{const option=document.createElement('option');option.value=decile;option.textContent='D'+decile;option.selected=decile===data.default_threshold;select.appendChild(option)}}}});
      const map=L.map('priority-map',{{zoomControl:true,attributionControl:true,preferCanvas:true,scrollWheelZoom:true}});
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}',{{maxZoom:17,attribution:'Tiles © Esri',opacity:.68}}).addTo(map);
      const classify=feature=>{{const hot=feature.properties.lst_decile>=Number(lstSelect.value);const vulnerable=feature.properties.vulnerability_decile>=Number(vulnerabilitySelect.value);return hot&&vulnerable?'both':hot?'heat':vulnerable?'vulnerability':'none'}};
      const colors={{both:'#d7191c',heat:'#f4a261',vulnerability:'#8e63b0',none:'#d9d9d9'}};
      const labels={{both:'Alta exposición + alta vulnerabilidad',heat:'Alta exposición térmica',vulnerability:'Alta vulnerabilidad',none:'Sin doble condición'}};
      const escapeHtml=value=>String(value).replace(/[&<>\"']/g,char=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}}[char]));
      let layer=null;
      const style=feature=>({{color:'rgba(255,255,255,.9)',weight:.55,fillColor:colors[classify(feature)],fillOpacity:.82}});
      const update=()=>{{
        const counts={{both:0,heat:0,vulnerability:0,none:0}};
        layer.eachLayer(item=>{{const category=classify(item.feature);counts[category]++;item.setStyle(style(item.feature));item.setTooltipContent('<strong>'+escapeHtml(item.feature.properties.census_id)+'</strong><br>'+labels[category]+'<br>LST: '+Number(item.feature.properties.lst).toFixed(2)+' °C · D'+item.feature.properties.lst_decile+'<br>Vulnerabilidad: '+Number(item.feature.properties.vulnerability_score).toFixed(1)+'/100 · D'+item.feature.properties.vulnerability_decile)}});
        document.getElementById('priority-summary').textContent=counts.both+' secciones con doble condición';
      }};
      layer=L.geoJSON(data.geojson,{{style,onEachFeature:(feature,item)=>{{item.bindTooltip('',{{sticky:true}});item.on({{mouseover:event=>event.target.setStyle({{weight:1.8,color:'#0000ff',fillOpacity:.92}}),mouseout:event=>event.target.setStyle(style(event.target.feature))}})}}}}).addTo(map);
      lstSelect.addEventListener('change',update);vulnerabilitySelect.addEventListener('change',update);
      map.fitBounds(data.bounds,{{padding:[8,8]}});update();
      const fit=()=>{{map.invalidateSize();if(window.frameElement)window.frameElement.style.height=(stage.offsetHeight+4)+'px'}};
      try{{const saved=JSON.parse(localStorage.getItem('urbanheat-thermal-social-priority-size-v1'));if(saved){{stage.style.width=saved.width;stage.style.height=saved.height}}}}catch(_){{}}
      const resize=document.querySelector('.priority-resize');
      resize.addEventListener('pointerdown',event=>{{event.preventDefault();event.stopPropagation();resize.setPointerCapture?.(event.pointerId);const sx=event.clientX,sy=event.clientY,sw=stage.offsetWidth,sh=stage.offsetHeight;
        const move=next=>{{next.preventDefault();stage.style.width=Math.max(520,sw+next.clientX-sx)+'px';stage.style.height=Math.max(420,sh+next.clientY-sy)+'px';fit()}};
        const end=()=>{{window.removeEventListener('pointermove',move,true);window.removeEventListener('pointerup',end,true);localStorage.setItem('urbanheat-thermal-social-priority-size-v1',JSON.stringify({{width:stage.style.width,height:stage.style.height}}));fit()}};
        window.addEventListener('pointermove',move,true);window.addEventListener('pointerup',end,true);
      }},true);
      window.addEventListener('resize',fit);fit();
    </script>
    """


def render_thermal_social_priority_map() -> None:
    path = ASSETS / "maps" / "thermal_social_priority.json"
    if not path.exists():
        st.warning("Aún no se ha preparado el mapa de prioridad térmico-social.")
        return
    components.html(_thermal_social_priority_map_html(), height=764, scrolling=False)


def render_modelizacion_visualizacion_slide_deck() -> None:
    """Estructura: HTML, mapa interactivo y mapa interactivo."""
    with st.container(key="modelizacion_visualizacion_slide_deck"):
        with st.container(key="modelizacion_visualizacion_slide_1"):
            render_object_canvas_editor("modelizacion_visualizacion_html")
        with st.container(key="modelizacion_visualizacion_slide_2"):
            render_model_comparison_map()
        with st.container(key="modelizacion_visualizacion_slide_3"):
            render_model_error_difference_map()


def render_sociodemografico_vulnerabilidad_hybrid() -> None:
    """Una pantalla híbrida: lienzo HTML a la izquierda y mapa a la derecha."""
    html_column, map_column = st.columns([2, 3], gap="small", vertical_alignment="top")
    with html_column:
        render_object_canvas_editor("sociodemografico_vulnerabilidad_html")
    with map_column:
        render_thermal_social_priority_map()


def render_scope_slide() -> None:
    """Slide HTML única de Scope."""
    render_object_canvas_editor("scope")


def render_target_lst_slide_deck() -> None:
    """Dos slides HTML independientes para Target LST."""
    with st.container(key="target_lst_slide_deck"):
        with st.container(key="target_lst_slide_1"):
            render_object_canvas_editor("target_lst_1")
        with st.container(key="target_lst_slide_2"):
            render_object_canvas_editor("target_lst_2")


def render_topomorphological_slide_deck() -> None:
    """Dos slides HTML independientes para Topomorfológicas."""
    with st.container(key="topomorfologicas_slide_deck"):
        with st.container(key="topomorfologicas_slide_1"):
            render_object_canvas_editor("topomorfológicas")
        with st.container(key="topomorfologicas_slide_2"):
            render_object_canvas_editor("topomorfológicas_2")


def render_land_cover_slide_deck() -> None:
    """Dos slides HTML independientes para Land Cover."""
    with st.container(key="land_cover_slide_deck"):
        with st.container(key="land_cover_slide_1"):
            render_object_canvas_editor("land_cover")
        with st.container(key="land_cover_slide_2"):
            render_object_canvas_editor("land_cover_2")


def render_distancias_slide_deck() -> None:
    if st.session_state.get("presentation_mode", False):
        with st.container(key="distancias_slide_deck"):
            with st.container(key="distancias_slide_1"):
                render_distance_clusters_map()
            with st.container(key="distancias_slide_2"):
                render_object_canvas_editor("distancias_2")
        return
    """Deck mixto: solo materializa la slide Folium o la HTML que está activa."""
    slide_index = int(st.session_state.get("distancias_slide_index", 0)) % 2
    if slide_index == 0:
        render_distance_clusters_map()
    else:
        render_object_canvas_editor("distancias_2")


@st.cache_data(show_spinner=False)
def _distance_clusters_payload() -> dict:
    return json.loads((ASSETS / "maps" / "parks_refuges_clusters.json").read_text(encoding="utf-8"))


def _distance_clusters_map_html() -> str:
    data = _distance_clusters_payload()
    map_ = folium.Map(location=[41.387, 2.17], zoom_start=12, tiles="CartoDB positron", control_scale=True)
    folium.GeoJson(data["districts"], name="Distritos", style_function=lambda _: {"fillOpacity": 0.03, "weight": 1, "color": "#6f6f6f"}).add_to(map_)
    parks = MarkerCluster(name="Parques", disableClusteringAtZoom=16).add_to(map_)
    shelters = MarkerCluster(name="Refugios climáticos", disableClusteringAtZoom=16).add_to(map_)
    for point in data["parks"]:
        folium.CircleMarker([point["lat"], point["lon"]], radius=4, color="#16803c", fill=True, fill_opacity=.85, tooltip=f"Parque · {point['name']}").add_to(parks)
    for point in data["shelters"]:
        folium.CircleMarker([point["lat"], point["lon"]], radius=4, color="#0f62fe", fill=True, fill_opacity=.85, tooltip=f"Refugio climático · {point['name']}").add_to(shelters)
    folium.LayerControl(collapsed=False).add_to(map_)
    html = map_.get_root().render()
    resizing = """
    <style>
      html, body { margin: 0; overflow: hidden; background: #fff; }
      .urbanheat-map-stage { position: relative; width: 100%; min-height: 620px; overflow: hidden; background: #fff; }
      .folium-map { position:absolute !important; left: 0; top: 0; width: 100% !important; height: 620px !important; min-width: 280px; min-height: 240px;
        overflow: hidden; box-sizing: border-box; border:1px solid #f0f0f0; }
      .urbanheat-resize-handle { position:absolute; right:0; bottom:0; width:18px; height:18px; z-index:2000;
        cursor:nwse-resize; touch-action:none; background:linear-gradient(135deg, transparent 0 45%, #9d9d9d 46% 51%, transparent 52% 62%, #9d9d9d 63% 68%, transparent 69%); }
      .urbanheat-map-drag-handle { display:none; position:absolute; right:22px; bottom:0; width:18px; height:18px; z-index:2000;
        cursor:move; touch-action:none; border:1px solid #9d9d9d; background:rgba(255,255,255,.92); box-sizing:border-box; }
      .urbanheat-map-drag-handle::before { content:"↕"; position:absolute; inset:0; text-align:center; line-height:16px; font-size:12px; color:#111; transform:rotate(45deg); }
    </style>
    <script>
      const mapBox = document.querySelector('.folium-map');
      const stage = document.createElement('div');
      stage.className = 'urbanheat-map-stage';
      mapBox.parentNode.insertBefore(stage, mapBox);
      stage.appendChild(mapBox);
      const handle = document.createElement('div'); handle.className = 'urbanheat-resize-handle'; mapBox.appendChild(handle);
      const dragHandle = document.createElement('div'); dragHandle.className = 'urbanheat-map-drag-handle'; mapBox.appendChild(dragHandle);
      const storageKey = 'urbanheat-content-leftlimit-v1-distance_clusters_map';
      const globalLeftLimit = 120;
      const localLeftLimit = () => {
        const frameLeft = window.frameElement ? window.frameElement.getBoundingClientRect().left : 0;
        return globalLeftLimit - frameLeft;
      };
      try {
        const saved = JSON.parse(localStorage.getItem(storageKey));
        if (saved) {
          mapBox.style.setProperty('width', saved.width, 'important');
          mapBox.style.setProperty('height', saved.height, 'important');
          mapBox.style.setProperty('left', '0px', 'important');
          mapBox.style.setProperty('top', '0px', 'important');
        }
      } catch (_) {}
      const sync = () => {
        const left = 0;
        const top = 0;
        mapBox.style.setProperty('left', left + 'px', 'important');
        stage.style.minHeight = Math.max(620, top + mapBox.offsetHeight + 12) + 'px';
        localStorage.setItem(storageKey, JSON.stringify({
          width: mapBox.style.width || mapBox.offsetWidth + 'px',
          height: mapBox.style.height || mapBox.offsetHeight + 'px',
          left: left + 'px',
          top: top + 'px'
        }));
        window.dispatchEvent(new Event('resize'));
        if (window.frameElement) window.frameElement.style.height = (stage.offsetHeight + 2) + 'px';
      };
      handle.addEventListener('mousedown', (event) => {
        event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation();
        const startX = event.clientX, startY = event.clientY, startW = mapBox.offsetWidth, startH = mapBox.offsetHeight;
        const move = (next) => {
          next.preventDefault(); next.stopPropagation();
          mapBox.style.setProperty('width', Math.max(280, startW + next.clientX - startX) + 'px', 'important');
          mapBox.style.setProperty('height', Math.max(240, startH + next.clientY - startY) + 'px', 'important'); sync();
        };
        const finish = () => {
          document.removeEventListener('mousemove', move, true);
          document.removeEventListener('mouseup', finish, true);
        };
        document.addEventListener('mousemove', move, true);
        document.addEventListener('mouseup', finish, true);
      }, true);
      dragHandle.addEventListener('mousedown', (event) => {
        event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation();
        const startX = event.clientX, startY = event.clientY;
        const startLeft = parseFloat(mapBox.style.left || '0');
        const startTop = parseFloat(mapBox.style.top || '0');
        const move = (next) => {
          next.preventDefault(); next.stopPropagation();
          mapBox.style.setProperty('left', Math.max(localLeftLimit(), startLeft + next.clientX - startX) + 'px', 'important');
          mapBox.style.setProperty('top', (startTop + next.clientY - startY) + 'px', 'important');
          sync();
        };
        const finish = () => {
          document.removeEventListener('mousemove', move, true);
          document.removeEventListener('mouseup', finish, true);
        };
        document.addEventListener('mousemove', move, true);
        document.addEventListener('mouseup', finish, true);
      }, true);
      sync();
    </script>
    """
    return html.replace("</body>", resizing + "</body>")


def render_distance_clusters_map() -> None:
    if not (ASSETS / "maps" / "parks_refuges_clusters.json").exists():
        st.warning("Aún no se ha preparado el mapa de parques y refugios.")
        return
    components.html(_distance_clusters_map_html(), height=960, scrolling=False)
    data = _distance_clusters_payload()
    st.caption(f"{len(data['parks'])} parques y {len(data['shelters'])} refugios climáticos · agrupación interactiva de marcadores.")
