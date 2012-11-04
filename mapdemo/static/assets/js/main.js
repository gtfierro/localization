//var ROOT_DOMAIN = "http://128.32.130.216:8000";

var ROOT_DOMAIN = "http://localhost:8000";

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
		Vis.counts = Vis.svg.selectAll(".txt").data(Floor.zones);
		Vis.counts.enter()
			.append("div")
				.attr("class", "txt")
				.text(function(d){return d.count;})
				.style("left", function(d){ return (d.tl.x+parseInt(d.width/2))+"px";})
				.style("top", function(d){ return (d.tl.y+parseInt(d.height/2))+"px";});
		
		//update existing ones
		Vis.counts.text(function(d){return d.count;});
	},
	'drawDevice' : function(){
		//draw circles
		var circles = Vis.svg.selectAll(".ball").data(Floor.data, function(d){ return d.mac; });
		circles.enter()
			.insert("div")
				.attr("class", "ball")
				.style("top", function (d) { return d.y+"px";})
				.style("left", function (d) { return d.x+"px";});

		circles
			.transition().duration(2000)
				.style("top", function (d) { return d.y+"px";})
				.style("left", function (d) { return d.x+"px";});
		
		circles.exit()
			.transition().duration(1000)
				.remove();
	},
	'drawZones' : function(){
		//draw the zones
		Vis.zones = Vis.svg.selectAll(".rec").data(Floor.zones);
		Vis.zones.enter()
			.append("div")
				.attr("class", "rec")
				.style("width", "0px")
				.style("height", function(d){ return parseFloat(d.height-4)+"px";})
				.style("left", "0px")
				.style("top", "0px")
			.transition().duration(500)
				.style("width", function(d){ return parseFloat(d.width-4)+"px";})
				.style("left", function(d){ return d.tl.x+"px";})
				.style("top", function(d){ return d.tl.y+"px";});
	}
};
Vis.svg = d3.select("#visual");
Vis.svg
	.append("img")
		.attr("src", ROOT_DOMAIN+"/static/assets/img/floor4.png")
		.attr("top", "0px")
		.attr("left", "0px")
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

