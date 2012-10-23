var ROOT_DOMAIN = "http://128.32.156.60:8000";
//var ROOT_DOMAIN = "http://localhost:8000";

var Floor = {
	'data' : [],
	'update' : function(datalist){
		var zmaxlen = Floor.zones.length,
			dmaxlen = datalist.length;
		var i, zone;
		for ( i = 0 ; i < zmaxlen; i++){
			zone = Floor.zones[i];
			zone.count = 0;
		}
		Floor.data = datalist;
		for ( i = 0; i < dmaxlen; i++){
			Floor.place(Floor.data[i]);
		}
		Vis.drawText();
		Vis.drawDevice();
	},
	'zones' : [], //each zone should have keys {tl, tr, br, bl, width,height,x,y,devices}
	'generateZones' : function(l){
		var maxlen = l.length;
		var i, obj, current;
		for ( i = 0; i < maxlen; i++ ){
			current = l[i];
			obj = {};
			obj.tl = {'x':current[0][0], 'y':current[0][1]};
			obj.tr = {'x':current[1][0], 'y':current[1][1]};
			obj.br = {'x':current[2][0], 'y':current[2][1]};
			obj.bl = {'x':current[3][0], 'y':current[3][1]};
			obj.width = obj.tr.x - obj.tl.x;
			obj.height = obj.br.y - obj.tr.y;
			obj.count = 0;
			Floor.zones.push(obj);
		}
		//draw the zones on canvas
		Vis.drawZones();
		return Floor.zones;
	},
	'place' : function(c){
		//puts a device into a a corresponding zone
		var maxlen = Floor.zones.length;
		var i, zone;
		for ( i = 0; i < maxlen; i++){
			zone = Floor.zones[i];
			if ( c.x >= zone.tl.x && c.x <= zone.tr.x && c.y >= zone.tl.y && c.y <= zone.bl.y ){
				zone.count++;
				break;
			}
		}
	},
	'fetch' : function(){
		$.getJSON(ROOT_DOMAIN+'/data', function(data){
			Floor.update(data.data);
		});
	}
};

var Vis = {
	'drawText' : function(){
		//draw counts in zones ( this will need to be consistently updated )
		Vis.counts = Vis.svg.selectAll("text").data(Floor.zones);
		Vis.counts.enter()
			.append("text")
				.text(function(d){return d.count;})
				.attr("x", function(d){ return (d.tl.x+parseInt(d.width/2))+"px";})
				.attr("y", function(d){ return (d.tl.y+parseInt(d.height/2))+"px";})
				.attr("font-size", "25px")
				.attr("font-family", "sans-serif")
				.attr("fill", "#fff");
		
		//update existing ones
		Vis.counts.text(function(d){return d.count;});
	},
	'drawDevice' : function(){
		//draw circles
		var circles = Vis.svg.selectAll("circle").data(Floor.data, function(d){ return d.mac; });
		circles.enter()
			.insert("circle")
				.attr("r", "0px")
				.attr("cx", function (d) { return d.x;})
				.attr("cy", function (d) { return d.y;})
				.attr("fill", "#4d90fe")
				.attr("r", "0px");

		circles
			.transition().duration(5000).ease("exp-in-out")
				.attr("r", "5px")
				.attr("cx", function (d) { return d.x;})
				.attr("cy", function (d) { return d.y;});
		
		circles.exit()
			.transition().duration(1000)
				.attr("r", 0)
				.remove();
	},
	'drawZones' : function(){
		//draw the zones
		Vis.zones = Vis.svg.selectAll("rect").data(Floor.zones);
		Vis.zones.enter()
			.append("rect")
				.attr("fill", "#ccc")
				.attr("stroke", "rgba(255,255,255,0.5)")
				.attr("stroke-width", "4")
				.attr("width", "0px")
				.attr("height", function(d){ return d.height+"px";})
				.attr("x", "0px")
				.attr("y", "0px")
				.attr("opacity", 0.8)
			.transition().duration(500)
				.attr("width", function(d){ return d.width+"px";})
				.attr("x", function(d){ return d.tl.x+"px";})
				.attr("y", function(d){ return d.tl.y+"px";});
	}
};
Vis.svg = d3.select("#visual");
Vis.svg
	.append("image")
		.attr("xlink:href", ROOT_DOMAIN+"/static/assets/img/floor4.png")
		.attr("x", "0px")
		.attr("y", "0px")
		.attr("width", "600px")
		.attr("height", "240px");


//create zones for vis
//Floor.generateZones(floordata.zones); //run this only once!!!!
//Floor.update(floordata.data);//update periodically
$.ajax({url:ROOT_DOMAIN+'/data', dataType: 'json', success:function(data){
	Floor.generateZones(data.zones);
	Floor.update(data.data);
	setInterval( Floor.fetch, 5000);
}});

