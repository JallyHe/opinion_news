// 日期的初始化
Date.prototype.format = function(format) {
    var o = {
        "M+" : this.getMonth()+1, //month 
        "d+" : this.getDate(),    //day 
        "h+" : this.getHours(),   //hour 
        "m+" : this.getMinutes(), //minute 
        "s+" : this.getSeconds(), //second 
        "q+" : Math.floor((this.getMonth()+3)/3),  //quarter 
        "S" : this.getMilliseconds() //millisecond 
    }
    if(/(y+)/.test(format)){
        format=format.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length));
    }
    for(var k in o){
        if(new RegExp("("+ k +")").test(format)){
            format = format.replace(RegExp.$1, RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length));
        }
    }
    return format;
}

function Opinion_timeline(query, start_ts, end_ts){
	this.query = query;
	this.start_ts = start_ts;
	this.end_ts = end_ts;
	this.max_keywords_size = 20; // 和计算相关的50，实际返回10
    this.min_keywords_size = 5;
    this.top_weibos_limit = 50; // 和计算相关的50，实际返回10
	this.timeLine_ajax_url = function(query, start_ts, end_ts){
		return "/news/eventriver/?query=" + query;
	}
	this.pie_ajax_url = function(query, start_ts, end_ts){
		return "/news/ratio/?query=" + query;
	}
	this.cloud_ajax_url = function(query, start_ts, end_ts){
		return "/news/keywords/?query=" + query;
	}
	this.weibo_ajax_url = function(query, start_ts, end_ts){
		return "/news/weibos/?query=" + query;
	}
	this.ajax_method = "GET";
	this.call_sync_ajax_request = function(url, method, callback){
        $.ajax({
            url: url,
            type: method,
            dataType: "json",
            async: false,
            success: callback
        })
    }
}

Opinion_timeline.prototype.pull_timeline_data = function(){
	var that = this; //向下面的函数传递获取的值
	var ajax_url = this.timeLine_ajax_url(this.query, this.start_ts, this.end_ts); //传入参数，获取请求的地址
	//console.log('timeline');
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Timeline_function); //发起ajax的请求
	
	function Timeline_function(data){    //数据的处理函数
		drawSubeventTab(data);
		event_river(data);
	} 
}

Opinion_timeline.prototype.pull_pie_data = function(){
	var that = this;
	var ajax_url = this.pie_ajax_url(this.query, this.start_ts, this.end_ts);
	//console.log('pie');
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Pie_function);
	
	function Pie_function(data){    //数据的处理函数
		//console.log(data);
		refreshPiedata(data);
	} 
}

Opinion_timeline.prototype.pull_cloud_data = function(){
	var that = this;
	var ajax_url = this.cloud_ajax_url(this.query, this.start_ts, this.end_ts);
	//console.log('cloud');
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Cloud_function);

	function Cloud_function(data){    //数据的处理函数
	
		refreshDrawKeywords(that, data);
	} 
}

Opinion_timeline.prototype.pull_weibo_data = function(){
	var that = this;
	var ajax_url = this.weibo_ajax_url(this.query, this.start_ts, this.end_ts);

	this.call_sync_ajax_request(ajax_url, this.ajax_method, Weibo_function);

	function Weibo_function(data){  
		refreshWeibodata(data);
	} 
}

//事件流的展示
function event_river(data){
    option = {
	    title : {
	        text: '事件流',
	        //subtext: '纯属虚构'
	    },
	    tooltip : {
	        trigger: 'item',
	        enterable: true
	    },
	    legend: {
	        data:[data['name']]
	    },
	    toolbox: {
	        show : true,
	        feature : {
	            mark : {show: true},
	            restore : {show: true},
	            saveAsImage : {show: true}
	        }
	    },
	    xAxis : [
	        {
	            type : 'time',
	            boundaryGap: [0.05,0.1]
	        }
	    ],
	    series : [data]
	};
    var myChart = echarts.init(document.getElementById('event_river'));
    myChart.setOption(option);       
}

function refreshPiedata(data){
	//console.log(data);
	var pie_data = [];
	var One_pie_data = {};
	for (var key in data){ 
		One_pie_data = {'value': data[key], 'name': key + (data[key]*100).toFixed(2)+"%"};
		pie_data.push(One_pie_data);		
	}

    option = {
        title : {
            text: '',
            x:'center', 
            textStyle:{
            fontWeight:'lighter',
            fontSize: 13,
            }        
        },
        toolbox: {
	        show : true,
	        feature : {
	         	mark : {show: true},
	           	dataView : {show: true, readOnly: false},
	            restore : {show: true},            
	            saveAsImage : {show: true}
	        }
    	},
        calculable : true,
        series : [
            {
                name:'访问来源',
                type:'pie',
                radius : '50%',
                center: ['50%', '60%'],
                data: pie_data
            }
        ]
    };
    var myChart = echarts.init(document.getElementById('main'));
    myChart.setOption(option);
}
// 画关键词云图
function refreshDrawKeywords(that, keywords_data){
    var min_keywords_size = that.min_keywords_size;
    var max_keywords_size = that.max_keywords_size;
    var keywords_div_id = 'keywords_cloud_div';
   	var color = '#11c897';
   	var data = keywords_data;
   	var value = [];
	var key = [];
    $("#"+keywords_div_id).empty();	
	if (data=={}){
	    $('#'+div_id_cloud).append("<a style='font-size:1ex'>关键词云数据为空</a>");
	}
	else{
	    var min_count, max_count = 0, words_count_obj = {};
		for (var subeventid in data){
			value = data[subeventid];
			word = value[0][0];
			count = value[0][1];

		// for (var subeventid in data){
		// 	value = data[subeventid];
		// 	one_subevent = value[1];
		// for (var word in one_subevent){
		// 	count = one_subevent(word);
		// }
		// }
	      	if(count > max_count){
	                max_count = count;
	        }
	      	if(!min_count){
	                min_count = count;
	        }
	      	if(count < min_count){
	                min_count = count;
	        }
	    	words_count_obj[word] = count;
		}
	    for(var keyword in words_count_obj){
	        var count = words_count_obj[keyword];
	        var size = defscale(count, min_count, max_count, min_keywords_size, max_keywords_size);
	        $('#'+keywords_div_id).append('<a><font style="color:' + color +  '; font-size:' + size + 'px;">' + keyword + '</font></a>');
	    }
	    	on_load(keywords_div_id);
	}
}
// 根据权重决定字体大小
function defscale(count, mincount, maxcount, minsize, maxsize){
    if(maxcount == mincount){
        return (maxsize + minsize) * 1.0 / 2
    }else{
        return minsize + 1.0 * (maxsize - minsize) * Math.pow((count / (maxcount - mincount)), 2)
    }
}

//把子话题输出
function drawSubeventTab(data){
    data = data['eventList'];
    var html = '<div class="btn-group btn-group-justified">';
    for (var i = 0;i < data.length;i++) {
        var begin_time = data[i]['evolution'][0]['time']; //开始时间
        var name = data[i]['name']; 
        html += '<div class="btn-group">';
        html += '<button type="button" class="btn btn-default">' + name + '</button>';
        html += '</div>';
    }
    html += '</div>';
    $("#checkbox").append(html);
}

function refreshWeibodata(data){  //需要传过来的是新闻的data
    $("#weibo_ul").empty();
	var html = "";
	for(var c_topic in data){
		var da = data[c_topic];
        for ( e in da){
            var d = da[e][1];
            var content_summary = d['content168'].substring(0, 168) + '...';
            if (d['same_list'] == undefined){
                var same_text_count = 0;
            }
            else{
                var same_text_count = d['same_list'].length;
            }
            html += '<li class="item" style="width:1010px">';
            html += '<div class="weibo_detail" >';
            html += '<p>媒体:<a class="undlin" target="_blank" href="javascript;;">' + d['source_from_name'] + '</a>&nbsp;&nbsp;发布:';
            html += '<span class="title" style="color:#0000FF" id="' + d['_id'] + '"><b>[' + d['title'] + ']</b></span>';
            html += '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;<span id="content_summary_' + d['_id']  + '">' + content_summary + '</span>';
            html += '<span style="display: none;" id="content_' + d['_id']  + '">' + d['content168'] + '&nbsp;&nbsp;</span>';
            html += '</p>';
            html += '<div class="weibo_info">';
        	html += '<div class="weibo_pz" style="margin-right:10px;">';
        	html += '<span id="detail_' + d['_id'] + '"><a class="undlin" href="javascript:;" target="_blank" onclick="detail_text(\'' + d['_id'] + '\')";>阅读全文</a></span>&nbsp;&nbsp;|&nbsp;&nbsp;';
        	html += '<a class="undlin" href="javascript:;" target="_blank" onclick="open_same_list(\'' + d['_id'] + '\')";>相似新闻(' + same_text_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        	html += "</div>";
        	html += '<div class="m">';
        	html += '<a class="undlin" target="_blank" >' + new Date(d['timestamp'] * 1000).format("yyyy-MM-dd hh:mm:ss")  + '</a>&nbsp;-&nbsp;';
        	html += '<a target="_blank">转载于'+ d["transmit_name"] +'</a>&nbsp;&nbsp;';
        	html += '</div>';
        	html += '</div>' 
            html += '</div>';
            html += '</li>';
            for (var i=0;i<same_text_count;i++){
                var dd = d['same_list'][i];
                html += '<div class="inner-same inner-same-' + d['_id'] + '" style="display:none;">';
                html += '<li class="item" style="width:1010px">';
	            html += '<div class="weibo_detail" >';
	            html += '<p>媒体:<a class="undlin" target="_blank" href="javascript;;">' + dd['source_from_name'] + '</a>&nbsp;&nbsp;发布:';
	            html += '<span class="title" style="color:#0000FF" id="' + dd['_id'] + '"><b> ' + dd['title'] + ' </b></span>';
	            html += '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;<span id="content_summary_' + d['_id']  + '">' + dd['content168'].substring(0, 168) + '...</span>';
	            html += '<span style="display: none;" id="content_' + dd['_id']  + '">' + d['content168'] + '&nbsp;&nbsp;</span>';
	            html += '</p>';
	            html += '<div class="weibo_info">';
	        	html += '<div class="weibo_pz" style="margin-right:10px;">';
	        	html += '<span id="detail_' + dd['_id'] + '"><a class="undlin" href="javascript:;" target="_blank" onclick="detail_text(\'' + dd['_id'] + '\')";>阅读全文</a></span>&nbsp;&nbsp;|&nbsp;&nbsp;';
	        	html += "</div>";
	        	html += '<div class="m">';
	        	html += '<a class="undlin" target="_blank" >' + new Date(dd['timestamp'] * 1000).format("yyyy-MM-dd hh:mm:ss")  + '</a>&nbsp;-&nbsp;';
	        	html += '<a target="_blank">转载于'+ dd["transmit_name"] +'</a>&nbsp;&nbsp;';
	        	html += '</div>';
	        	html += '</div>' 
	            html += '</div>';
	            html += '</li>';
                html += '</div>';
            }
        }
    }
    $("#weibo_ul").append(html);
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

function summary_text(text_id){
    $("#content_summary_" + text_id).css("display", "inline");
    $("#content_" + text_id).css("display", "none");
    $("#detail_" + text_id).html("<a href= 'javascript:;' target='_blank' onclick=\"detail_text(\'" + text_id + "\');\">阅读全文</a>&nbsp;&nbsp;");
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

function detail_text(text_id){
    $("#content_summary_" + text_id).css("display", "none");
    $("#content_" + text_id).css("display", "inline");
    $("#detail_" + text_id).html("<a href= 'javascript:;' target='_blank' onclick=\"summary_text(\'" + text_id + "\');\">阅读概述</a>&nbsp;&nbsp;");
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

function open_same_list(text_id){
    $(".inner-same-" + text_id).each(function(){
        if( $(this).css("display") == "none"){
            $(this).css("display", "inline");
        }
        else{
            $(this).css("display", "none");
        }
    });
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

//画关键字表格的代码，现在已经没有了
function drawtable(data){
    var topic_child_keywords = {};
    var html = '';
    var target_html = '';
    var m = 0;
    var number;                  
    for (var key in data){
        topic_child_keywords[key] = [];
        for (var i = 0; i < data[key].length; i++){
            topic_child_keywords[key].push(data[key][i][1]);
        }
    }
    
    for (var topic in topic_child_keywords){
        m++;
        if( m > 10) {
        	break;
        }
        html += '<tr style="height:25px">';                    
        html += '<td><b style =\"width:20px\">'+topic+'</b></td>';
        for (var n = 0 ;n < 5; n++){
            html += '<td>'+topic_child_keywords[topic][n]+'</td>'
        }
        html += "</tr>";
    }
    $("#alternatecolor").append(html);
}

var query = QUERY;
var start_ts = 1354896458;
var end_ts = 154686446564;
Timeline = new Opinion_timeline(query, start_ts, end_ts);
Timeline.pull_timeline_data();
Timeline.pull_cloud_data();
Timeline.pull_weibo_data();
Timeline.pull_pie_data();
