if(height){layout.height=height;}
layout.autosize=false;}
else if(autosize!==null){layout.autosize=autosize;}
if(layout.autosize){delete layout.width;delete layout.height;}
return layout;};Embed.prototype.getFrames=function(){return JSON.parse(d3.select('#plot-frames').text());};Embed.prototype.getDisplayLogo=function(){return d3.select('#plot-logo').text()==='true';};Embed.prototype.getDisplayModeBar=function(){var modebarMode=d3.select('#plot-modebar').text();switch(modebarMode){case'false':return false;case'hover':return'hover';default:return true;}};Embed.prototype.getMapboxAccessToken=function(){return d3.select('#plot-mapbox-access-token').text();};Embed.prototype.getDisplayLink=function(){return d3.select('#plot-link').text()==='true';};Embed.prototype.getIEVersion=function(){return document.documentMode?document.documentMode:0;};Embed.prototype.stopLoading=function(){d3.select('#plotlybars').remove();};Embed.prototype.initStream=function(graphDiv,Plotly){if(typeof StreamHead==='undefined'){return;}
var streamhead=new StreamHead(Plotly,graphDiv,{autoreload:true});streamhead.init();streamhead.connect({host:ENV.WEBSOCKET_HOST,port:ENV.WEBSOCKET_PORT});};Embed.prototype.initPostMessage=function(){var embed=this;window.addEventListener('message',function(ev){embed.onMessage(ev,embed);});};Embed.prototype.isShareplot=function(){if(window.self===window.top)return false;try{var myLocation=window.location.href,parentLocation=window.parent.location.href;return parentLocation.indexOf(myLocation.split('.embed')[0])===0;}
catch(e){return false;}};Embed.prototype.getConfig=function(){var isShareplot=this.isShareplot(),isTopFrame=window===window.top,bodyStyle=document.body.style;function setBodyTransparent(gd,bgColor){bodyStyle.backgroundColor=bgColor;if(!bodyStyle.backgroundColor){bodyStyle.backgroundColor='white';}}
function setBodyOpaque(gd,bgColor){bodyStyle.backgroundColor=Plotly.Color.combine(bgColor,'white');if(!bodyStyle.backgroundColor){bodyStyle.backgroundColor='white';}}
return{displaylogo:this.getDisplayLogo(),displayModeBar:this.getDisplayModeBar(),mapboxAccessToken:this.getMapboxAccessToken(),autosizable:true,fillFrame:true,sendData:false,showLink:this.getDisplayLink(),scrollZoom:isShareplot,setBackground:isTopFrame?setBodyOpaque:setBodyTransparent};};Embed.prototype.init=function(){if(this.inited)return;var showLink=true;if(window.location.href.indexOf('link=false')!==-1){showLink=false;}
if(showLink){document.getElementById('js-edit-link').style.display='block';}
var embed=this;embed.data=embed.getData();embed.layout=embed.getLayout();embed.frames=embed.getFrames();embed.config=embed.getConfig();embed.inited=true;return embed.initialPlot();};Embed.prototype.setUp=function(){var embed=this;embed.initPostMessage();document.addEventListener('DOMContentLoaded',function(){Raven.context(embed.getRavenConfig(),function(){embed.init();});});};Embed.prototype.initialPlot=function(){var embed=this;var graphDiv=embed.graphDiv;var minPlotWidth=100;var maxPlottingDelay=3000;var interval=50;return new Promise(function(resolve){if(graphDiv.clientWidth>minPlotWidth){resolve();return;}
var delay=0;var intervalID=setInterval(function(){delay+=interval;if(graphDiv.clientWidth>minPlotWidth||delay>maxPlottingDelay){clearInterval(intervalID);resolve();}},interval);}).then(function(){var plotDone=Plotly.plot(graphDiv,{data:embed.data,layout:embed.layout,frames:embed.frames,config:embed.config});embed.isReady=true;embed.resolveReady();return plotDone;}).then(function(){embed.stopLoading();embed.svgContainer=d3.select(graphDiv).select('.svg-container');window.addEventListener('resize',function(){embed.resizePlot();});d3.select('html').classed('is-iframe',true);embed.svgContainer.style('margin','auto');embed.initStream(graphDiv,Plotly);return Plotly.Breakpoints.apply(graphDiv,embed.data,embed.layout);}).then(function(){return Plotly.Plots.redrawText(graphDiv);});};Embed.prototype.resizePlot=function(){var embed=this;var graphDiv=embed.graphDiv;return new Promise(function(resolve){if(embed.layout.autosize){delete embed.layout.width;delete embed.layout.height;Plotly.Plots.resize(graphDiv).then(function(){graphDiv.style.background='none';return Plotly.Breakpoints.apply(graphDiv,embed.data,embed.layout);}).then(resolve);}
else resolve();});};Embed.prototype.onMessage=function(ev,embed){var message={source:ev.source,origin:ev.origin,data:ev.data},handler=Embed.handlers[message.data.task];if(handler){handler(embed,message);}else if(message.data.task){console.warn('Supplied task attribute not recognized',message.data);}};Embed.prototype.clonePoints=function(points){var clonedPoints=[];var point;for(var i=0;i<points.length;i++){point=points[i];clonedPoints[i]={data:point.data,curveNumber:point.curveNumber,pointNumber:point.pointNumber,x:point.x,y:point.y};}
return clonedPoints;};Embed.prototype.sendData=function(){this.graphDiv._context.sendData=true;Plotly.Plots.addLinks(this.graphDiv);};Embed.prototype.afterReady=function(callback){var embed=this;embed.readyPromise=embed.readyPromise.then(callback);return embed.readyPromise;};Embed.handlers={};Embed.handlers.newPlot=function(embed,message){embed.afterReady(function(){embed.sendData();Plotly.newPlot(embed.graphDiv,message.data.data,message.data.layout);});};Embed.handlers.restyle=function(embed,message){embed.afterReady(function(){embed.sendData();Plotly.restyle(embed.graphDiv,message.data.update,null,message.data.indices);});};Embed.handlers.relayout=function(embed,message){var update=message.data.update;if(embed.isReady){Plotly.relayout(embed.graphDiv,update);}
else{var layout=embed.layout;Object.keys(update).forEach(function(k){Plotly.Lib.nestedProperty(layout,k).set(update[k]);});}
if(message.data.sendData!==false){embed.afterReady(function(){embed.sendData();});}};Embed.handlers.hover=function(embed,message){embed.afterReady(function(){Plotly.Fx.hover(embed.graphDiv,message.data.selection,message.data.subplot);});};Embed.handlers.listen=function(embed,message){var graphDiv=embed.graphDiv;var zoomHandler=function(){Embed.postRanges(embed,message);};var hoverHandler=function(data){Embed.postPoints('hover',data,message);};var unhoverHandler=function(data){Embed.postPoints('unhover',data,message);};var clickHandler=function(data){Embed.postPoints('click',data,message);};graphDiv.removeListener('plotly_relayout',zoomHandler);graphDiv.removeListener('plotly_hover',hoverHandler);graphDiv.removeListener('plotly_unhover',unhoverHandler);graphDiv.removeListener('plotly_click',clickHandler);if(message.data.events.indexOf('zoom')!==-1){graphDiv.on('plotly_relayout',zoomHandler);}
if(message.data.events.indexOf('hover')!==-1){graphDiv.on('plotly_hover',hoverHandler);graphDiv.on('plotly_unhover',unhoverHandler);}
if(message.data.events.indexOf('click')!==-1){graphDiv.on('plotly_click',clickHandler);}};Embed.handlers.addTraces=function(embed,message){embed.afterReady(function(){embed.sendData();Plotly.addTraces(embed.graphDiv,message.data.traces,message.data.newIndices);});};Embed.handlers.deleteTraces=function(embed,message){embed.afterReady(function(){embed.sendData();Plotly.deleteTraces(embed.graphDiv,message.data.indices);});};Embed.handlers.moveTraces=function(embed,message){embed.afterReady(function(){embed.sendData();Plotly.moveTraces(embed.graphDiv,message.data.currentIndices,message.data.newIndices);});};Embed.handlers.extendTraces=function(embed,message){embed.afterReady(function(){var data=message.data;Plotly.extendTraces(embed.graphDiv,data.update,data.indices,data.maxPoints);});};Embed.handlers.getLayout=function(embed,message){var layout=embed.getLayout();if((!layout.width||!layout.height)&&message.data.layout){d3.select('#plot-width').text(message.data.layout.width);d3.select('#plot-height').text(message.data.layout.height);d3.select('#plot-autosize').text('true');layout=embed.getLayout();}
Embed.postMessage(message,{'layout':layout,'id':message.data.id});};Embed.handlers.getAttributes=function(embed,message){embed.afterReady(function(){var resObj={},value,attributes,graph,i;graph=Plotly.Plots.graphJson(embed.graphDiv,false,null,'object',true);if(typeof message.data.attributes==='string'){attributes=[message.data.attributes];}else{attributes=message.data.attributes||['data','layout'];}
if(Array.isArray(attributes)){for(i=0;i<attributes.length;i++){value=Plotly.Lib.nestedProperty(graph,attributes[i]).get();resObj[attributes[i]]=value;}}else{resObj=graph;}
Embed.postMessage(message,{task:'getAttributes',response:resObj});});};Embed.handlers.setAutosize=function(embed,message){embed.layout.autosize=!!message.data.value;};Embed.handlers.ping=function(embed,message){Embed.postMessage(message,{'pong':true});};Embed.handlers.redraw=function(embed){if(embed.isReady){Plotly.redraw(embed.graphDiv);}};Embed.postRanges=function(embed,message){var returnMessage={type:'zoom',ranges:{}};Plotly.Axes.list(embed.graphDiv).forEach(function(ax){returnMessage.ranges[ax._id]=ax.range.map(ax.l2c);});Embed.postMessage(message,returnMessage);};Embed.postPoints=function(evtName,data,message){var returnMessage={type:evtName,points:Embed.prototype.clonePoints(data.points)};Embed.postMessage(message,returnMessage);};Embed.postMessage=function(message,obj){message.source.postMessage(obj,message.origin);};}(ENV,window));