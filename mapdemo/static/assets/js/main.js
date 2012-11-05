//var ROOT_DOMAIN = "http://128.32.130.216:8000";

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
		$.getJSON('/client_data', function(data){
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
				.style("width", "0px")
				.style("height", "0px")
				.style("border", function(d){
					if ( d.ip === MY_IP ){
						return "2px solid #D84A0F";
					}else{
						return "2px solid #FFF";
					}
				})
				.style("top", function (d) { return d.y+"px";})
				.style("left", function (d) { return d.x+"px";});

		circles
			.transition().duration(700)
				.style("margin-left", "-5px")
				.style("margin-top", "-5px")
				.style("width", "10px")
				.style("height", "10px")
				.style("background-color", function(d){
					if ( d.h === undefined || d.s === undefined || d.l === undefined ){
						return "#4d90fe";
					}else{
						return d3.hsl(d.h,d.s,d.l).toString();
					}
				})
				.style("top", function (d) { return d.y+"px";})
				.style("left", function (d) { return d.x+"px";});
		
		circles.exit()
			.transition().duration(700)
				.style("width", "0px")
				.style("height", "0px")
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
		.attr("src","/static/assets/img/floorplan.png")
		.attr("top", "0px")
		.attr("left", "0px")
		.attr("width", "750px")
		.attr("height", "341px");

/*Vis.toggle = {};
Vis.toggle.zones = {
	state : 1, //1 is on, 0 is off
	switch : function(){
		if ( Vis.toggle.zones.state === 1 ){
			return;
		}else{
			return;
		}
	}
};
Vis.toggle.zones = {};*/
//create zones for vis
//Floor.generateZones(floordata.zones); //run this only once!!!!
//Floor.update(floordata.data);//update periodically
$.ajax({url:'/zone_data', dataType: 'json', success:function(data){
	Floor.generateZones(data.zones);
	Floor.fetch();
	setInterval( Floor.fetch, 5000);
}});

Vis.color = $.farbtastic("#picker", function(cc){
	var pref = {"h":Vis.color.hsl[0]*360,"s":Vis.color.hsl[1],"l":Vis.color.hsl[2]};
	$('#colorbox').css('background-color', cc);
	d3.selectAll(".ball").data(Floor.data, function(d){ return d.mac; }).transition().duration(500)
		.style("background-color", function(d){
			if ( d.ip === MY_IP ){
				return cc;
			}else{
				if ( d.h === undefined || d.s === undefined || d.l === undefined ){
					return "#4d90fe";
				}else{
					return d3.hsl(d.h,d.s,d.l).toString();
				}
			}
		});
	$.ajax({
		url:'/update_pref',
		data: pref,
		success: function(){return;},
		error:function(){alert("Something went wrong..");}
	});
});


$.getJSON('/client_data', function(data){
	var current = _.filter(data.data, function(d){return d.ip === MY_IP;});
	var d = current[0]
	if (current.length !== 0){
		Vis.color.setColor(d3.hsl(d.h,d.s,d.l).toString());
	}else{
		$("#colorpref").hide();
	}
});

