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

function Opinion_timeline(query, start_ts, end_ts, pointInterval){
	this.query = query;
	this.start_ts = start_ts;
	this.end_ts = end_ts;
    this.pointInterval = pointInterval; // 图上一点的时间间隔
	this.eventriver_ajax_url = function(query, end_ts, during){
		return "/news/eventriver/?query=" + query + "&during=" + during + "&ts=" + end_ts;
	}
	this.pie_ajax_url = function(query, end_ts, during, subevent){
		return "/news/ratio/?query=" + query + "&subevent=" + subevent + "&during=" + during + "&ts=" + end_ts;
	}
	this.cloud_ajax_url = function(query, end_ts, during, subevent){
		return "/news/keywords/?query=" + query + "&subevent=" + subevent + "&during=" + during + "&ts=" + end_ts;
	}
	this.weibo_ajax_url = function(query, end_ts, during, subevent){
		return "/news/weibos/?query=" + query + "&topk=10" + "&ts=" + end_ts + "&during=" + during + "&subevent=" + subevent;
	}
    this.peak_ajax_url = function(data, ts_list, during, subevent){
        return "/news/peak/?lis=" + data.join(',') + "&ts=" + ts_list + '&during=' + during + "&subevent=" + subevent;
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

    this.trend_div_id = 'trend_div';
    this.trend_title = '热度走势图';
    this.trend_chart;

    this.event_river_data; // 接收eventriver的数据
    this.select_subevent; // 当前选择的subevent, global表示总体，subeventid表示各子事件

    this.click_status = 'global'; // 标识当前的状态，global表示全局，peak表示点击了某个拐点后的情况

    var that = this;
    $("#clickalltime").click(function(){
        $("#cloudpie").css("display", "block");
        that.drawTrendline();
        that.pullDrawPiedata();
        that.pullDrawClouddata();
        that.pullDrawWeibodata();
    });

    this.trend_count_obj = {
        "ts": [],
        "count": []
    };

    this.weibo_data = []; // 存储新闻信息，便于前端排序
    $("#sort_by_timestamp").click(function(){
        that.weibo_data.sort(news_timestamp_comparator);
        refreshWeibodata(that.weibo_data);
        $("#sort_by_timestamp").css("color", "#333");
        $("#sort_by_weight").css("color", "-webkit-link");
    });
    $("#sort_by_weight").click(function(){
        that.weibo_data.sort(news_weight_comparator);
        refreshWeibodata(that.weibo_data);
        $("#sort_by_weight").css("color", "#333");
        $("#sort_by_timestamp").css("color", "-webkit-link");
    });
}

function news_timestamp_comparator(a, b) {
    return parseInt(b.timestamp) - parseInt(a.timestamp);
}

function news_weight_comparator(a, b) {
    return parseInt(b.weight) - parseInt(a.weight);
}

Opinion_timeline.prototype.pull_eventriver_data = function(){
	var that = this; //向下面的函数传递获取的值
	var ajax_url = this.eventriver_ajax_url(this.query, this.end_ts, this.end_ts - this.start_ts); //传入参数，获取请求的地址

	this.call_sync_ajax_request(ajax_url, this.ajax_method, Timeline_function); //发起ajax的请求
	
	function Timeline_function(data){    //数据的处理函数
        that.event_river_data = data;
        that.select_subevent = 'global'; // 默认处理总体
        subevent_list = data['eventList'];
    }
}

// 绘制子事件Tab
Opinion_timeline.prototype.drawSubeventsTab = function(){
    var that = this;
    drawSubeventTab(this.event_river_data, that); // 画子事件Tab
}

// 绘制eventriver
Opinion_timeline.prototype.drawEventriver = function(){
    drawEventstack(this.event_river_data); // 主题河
}

// instance method, 获取数据并绘制趋势图
Opinion_timeline.prototype.drawTrendline = function(){
    var trends_title = this.trend_title;
    var trend_div_id = this.trend_div_id;
    var pointInterval = this.pointInterval;
    var start_ts = this.start_ts;
    var end_ts = this.end_ts;
    var xAxisTitleText = '时间';
    var yAxisTitleText = '数量';
    var series_data = [{
            name: '新闻数',
            data: [],
            id: 'count',
            color: '#11c897',
            marker : {
                enabled : false,
            }
        },
        {
            name: '拐点',
            type : 'flags',
            data : [],
            cursor: 'pointer',
            onSeries : 'count',
            shape : 'circlepin',
            width : 2,
            color: '#fa7256',
            visible: true, // 默认显示绝对
            showInLegend: true
        }]

    var that = this;
    myChart = display_trend(that, trend_div_id, this.query, pointInterval, start_ts, end_ts, trends_title, series_data, xAxisTitleText, yAxisTitleText);
    this.trend_chart = myChart;
}

Opinion_timeline.prototype.pullDrawPiedata = function(){
	var that = this;
	var ajax_url = this.pie_ajax_url(this.query, this.start_ts, this.end_ts, this.select_subevent);
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Pie_function);
	
	function Pie_function(data){    //数据的处理函数
		refreshPiedata(data);
	} 
}

Opinion_timeline.prototype.pullDrawClouddata = function(){
	var that = this;
	var ajax_url = this.cloud_ajax_url(this.query, this.end_ts, this.end_ts - this.start_ts, this.select_subevent);
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Cloud_function);

    function Cloud_function(data){    //数据的处理函数
        refreshDrawKeywords(that, data);
    }
}

Opinion_timeline.prototype.pullDrawWeibodata = function(){
	var that = this;
	var ajax_url = this.weibo_ajax_url(this.query, this.end_ts, this.end_ts - this.start_ts, this.select_subevent);

	this.call_sync_ajax_request(ajax_url, this.ajax_method, Weibo_function);

    function Weibo_function(data){
        that.weibo_data = data;
        refreshWeibodata(data);
    }
}

// 走势图
function display_trend(that, trend_div_id, query, during, begin_ts, end_ts, trends_title, series_data, xAxisTitleText, yAxisTitleText){
    if($('#' + trend_div_id).highcharts()){
        var chart_series = $('#' + trend_div_id).highcharts().series;
        for(var i=0;i < chart_series.length; i++){
            chart_series[i].remove();
        }
        $('#' + trend_div_id).highcharts().destroy();
    }
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    var chart_obj = $('#' + trend_div_id).highcharts({
        chart: {
            type: 'spline',// line,
            animation: Highcharts.svg, // don't animate in old IE
            style: {
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            },
            events: {
                load: function() {
                    var total_nodes = (end_ts - begin_ts) / during;
                    var times_init = 0;

                    var count_series = this.series[0];
                    var absolute_peak_series = this.series[1];
                    pull_emotion_count(that, query, that.select_subevent, total_nodes, times_init, begin_ts, during, count_series, absolute_peak_series);
                }
            }
        },
        plotOptions:{
            line:{
                events: {
                    legendItemClick: function () {
                    }
                }
            }
        },
        title : {
            text: '走势分析图', // trends_title
            margin: 20,
            style: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '14px',
                fontFamily: 'Microsoft YaHei'
            }
        },
        // 导出按钮汉化
        lang: {
            printChart: "打印",
            downloadJPEG: "下载JPEG 图片",
            downloadPDF: "下载PDF文档",
            downloadPNG: "下载PNG 图片",
            downloadSVG: "下载SVG 矢量图",
            exportButtonTitle: "导出图片"
        },
        rangeSelector: {
            selected: 4,
            inputEnabled: false,
            buttons: [{
                type: 'week',
                count: 1,
                text: '1w'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'month',
                count: 3,
                text: '3m'
            }]
        },
        xAxis: {
            title: {
                enabled: true,
                text: xAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },
            type: 'datetime',
            tickPixelInterval: 150
        },
        yAxis: {
            min: 0,
            title: {
                enabled: true,
                text: yAxisTitleText,
                style: {
                    color: '#666',
                    fontWeight: 'bold',
                    fontSize: '12px',
                    fontFamily: 'Microsoft YaHei'
                }
            },
        },
        tooltip: {
            valueDecimals: 2,
            xDateFormat: '%Y-%m-%d %H:%M:%S'
        },
        legend: {
            layout: 'horizontal',
            //verticalAlign: true,
            //floating: true,
            align: 'center',
            verticalAlign: 'bottom',
            x: 0,
            y: -2,
            borderWidth: 1,
            itemStyle: {
                color: '#666',
                fontWeight: 'bold',
                fontSize: '12px',
                fontFamily: 'Microsoft YaHei'
            }
            //enabled: true,
            //itemHiddenStyle: {
                //color: 'white'
            //}
        },
        exporting: {
            enabled: true
        },
        series: series_data
    });
    return chart_obj;
}

function pull_emotion_count(that, query, emotion_type, total_days, times, begin_ts, during, count_series, absolute_peak_series){
    if(times > total_days){
        get_peaks(that, absolute_peak_series, that.trend_count_obj['count'], that.trend_count_obj['ts'], during);
        return;
    }

    var ts = begin_ts + times * during;
    var ajax_url = "/news/timeline/?ts=" + ts + '&during=' + during + '&subevent=' + emotion_type + '&query=' + query;
    $.ajax({
        url: ajax_url,
        type: "GET",
        dataType:"json",
        success: function(data){
            var isShift = false;
            var name = that.select_subevent;
            var ts = data[name][0];
            var count = data[name][1];
            count_series.addPoint([ts * 1000, count], true, isShift);
            that.trend_count_obj['ts'].push(ts);
            that.trend_count_obj['count'].push([ts * 1000, count]);
            times++;
            pull_emotion_count(that, query, emotion_type, total_days, times, begin_ts, during, count_series, absolute_peak_series);
        }
    });
}

function get_peaks(that, series, data_obj, ts_list, during){
    var name = that.select_subevent;
    var select_series = series;
    var data_list = data_obj;
    call_peak_ajax(that, select_series, data_list, ts_list, during, name);
}

function call_peak_ajax(that, series, data_list, ts_list, during, subevent){
    var data = [];
    for(var i in data_list){
        data.push(data_list[i][1]);
    }

    var ajax_url = that.peak_ajax_url(data, ts_list, during, subevent);
    that.call_sync_ajax_request(ajax_url, that.ajax_method, peak_callback);

    function peak_callback(data){
        var isShift = false;
        var flagClick = function(event){
            var click_ts = this.x / 1000;
            var title = this.title;
            $("#cloudpie").css("display", "none");
            that.click_status = 'peak';
            var ajax_url = that.weibo_ajax_url(that.query, click_ts, that.pointInterval, that.select_subevent);
            that.call_sync_ajax_request(ajax_url, that.ajax_method, Weibo_function);

            function Weibo_function(data){
                that.weibo_data = data;
                refreshWeibodata(data);
            }
        }
        for(var i in data){
            var x = data[i]['ts'];
            var title = data[i]['title'];
            series.addPoint({'x': x, 'title': title, 'text': '拐点' + title, 'events': {'click': flagClick}}, true, isShift);
        }
    }
}

//事件流的展示
function drawEventriver(data){
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

function drawEventstack(data){
	var data = data['eventList'];
	var series_data = [];
	var series_name = [];
	var One_series_data = {};
	var x_data = [];
	var temp_data = [];
	for (var k= 0; k < data.length; k++){
		One_series_value = [];
		One_series_time = [];
		temp_data = [];
		for(var i = 0; i < data[k]['evolution'].length; i++){
			One_series_value.push(data[k]['evolution'][i]['value']);
			temp_data.push(data[k]['evolution'][i]['value']);
			One_series_time.push(data[k]['evolution'][i]['time']);
			if(k == 0){
				x_data.push(data[k]['evolution'][i]['time']);
			}
		}
		if(One_series_value.length < x_data.length){
			for(var j = 0; j < x_data.length; j++){
				One_series_value[j] = 0;
				for(var m = 0; m < One_series_time.length; m++){
					if(x_data[j] == One_series_time[m]){
						One_series_value[j] = temp_data[m];
					}
				}
			}
		}

		One_series_data = {'name':data[k]['name'], 'type':'line', 'stack':'总量','itemStyle':{'normal': {'areaStyle': {'type': 'default'}}},  'data':One_series_value};
		series_name.push(One_series_data['name']);
		series_data.push(One_series_data);
	}

	option = {
	    tooltip : {
	        trigger: 'axis'
	    },
	    legend: {
	        data:series_name
	    },
	    calculable : true,
	    xAxis : [
	        {
	            type : 'category',
	            boundaryGap : false,
	            data : x_data
	        }
	    ],
	    yAxis : [
	        {
	            type : 'value'
	        }
	    ],
	    series : series_data
	        
	};
	var myChart = echarts.init(document.getElementById('event_river'));
    myChart.setOption(option); 
}

function refreshPiedata(data){
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
   	var value = [];
	var key = [];
    $("#"+keywords_div_id).empty();	
	if (keywords_data=={}){
	    $('#'+div_id_cloud).append("<a style='font-size:1ex'>关键词云数据为空</a>");
	}
	else{
	    var min_count, max_count = 0, words_count_obj = {};
		for (var word in keywords_data){
            var count = keywords_data[word];
	      	if(count > max_count){
	            max_count = count;
	        }
	      	if(!min_count){
	            min_count = count;
	        }
	      	if(count < min_count){
	            min_count = count;
	        }
		}
        words_count_obj = keywords_data;
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
function drawSubeventTab(data, that){
    var data = data['eventList'];
    var html = '';
    html += '<div class="btn-group" id="global">';
    html += '<button type="button" class="btn btn-success" style="margin: 5px;">' + query + '</button>';
    html += '</div>';
    for (var i = 0;i < data.length;i++) {
        var name = data[i]['name'];
        var weight = data[i]['weight'];
        var subeventid = data[i]['id'];
        html += '<div class="btn-group" id="' + subeventid + '">';
        html += '<button type="button" class="btn btn-default" style="margin: 5px;">' + name + '(' + weight + ')</button>';
        html += '</div>';
    }
    $("#subevent_tab").append(html);
    subevent_tab_click(that);
}

function subevent_tab_click(that){
    $div = $('#subevent_tab').children('div');
    $div.each(function(){
        $(this).click(function(){
            $('#subevent_tab').children('div').each(function(){
                if($("#" + this.id + " :button").hasClass("btn btn-success")){
                    $("#" + this.id + " :button").removeClass("btn btn-success").addClass("btn btn-default");
                }
            });
            $("#" + this.id + " :button").removeClass("btn btn-default").addClass("btn btn-success");
            change_subevent_stat(this.id, that);
        })
    })
}

function change_subevent_stat(subeventid, that){
    that.select_subevent = subeventid;
    that.drawTrendline();
    that.pullDrawClouddata();
    that.pullDrawPiedata();
    that.pullDrawWeibodata();
}

// 画重要微博
function refreshWeibodata(data){  //需要传过来的是新闻的data
    $("#weibo_ul").empty();
	var html = "";
    for ( e in data){
        var d = data[e];
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
        html += '<a class="undlin" href="javascript:;" target="_blank" onclick="open_same_list(\'' + d['_id'] + '\')";>相似新闻(' + same_text_count + ')</a>&nbsp;&nbsp;&nbsp;&nbsp;';
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
            html += '<li class="item" style="width:1000px; border:2px solid">';
            html += '<div class="weibo_detail" >';
            html += '<p>媒体:<a class="undlin" target="_blank" href="javascript;;">' + dd['source_from_name'] + '</a>&nbsp;&nbsp;发布:';
            html += '<span class="title" style="color:#0000FF" id="' + dd['_id'] + '"><b> ' + dd['title'] + ' </b></span>';
            html += '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;<span id="content_summary_' + d['_id']  + '">' + dd['content168'].substring(0, 168) + '...</span>';
            html += '<span style="display: none;" id="content_' + dd['_id']  + '">' + d['content168'] + '&nbsp;&nbsp;</span>';
            html += '</p>';
            html += '<div class="weibo_info">';
            html += '<div class="weibo_pz" style="margin-right:10px;">';
            html += '<span id="detail_' + dd['_id'] + '"><a class="undlin" href="javascript:;" target="_blank" onclick="detail_text(\'' + dd['_id'] + '\')";>阅读全文</a></span>&nbsp;&nbsp;&nbsp;&nbsp;';
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
var start_ts = START_TS;
var end_ts = END_TS;
var pointInterval = 3600 * 24;
var opinion = new Opinion_timeline(query, start_ts, end_ts, pointInterval);
opinion.pull_eventriver_data();
opinion.drawSubeventsTab();
opinion.drawEventriver();
opinion.drawTrendline();
opinion.pullDrawClouddata();
opinion.pullDrawWeibodata();
opinion.pullDrawPiedata();
