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
    this.weibo_limit_count = 10; // 每次加载10条微博
    this.weibo_skip = 0; // 当前页面已显示的微博数
    this.weibo_sort = "weight"; // 当前页面微博排序依据
	this.eventriver_ajax_url = function(query, end_ts, during){
		return "/news/eventriver/?query=" + query + "&during=" + during + "&ts=" + end_ts;
	}
	this.pie_ajax_url = function(query, end_ts, during, subevent){
		return "/news/ratio/?query=" + query + "&subevent=" + subevent + "&during=" + during + "&ts=" + end_ts;
	}
	this.cloud_ajax_url = function(query, end_ts, during, subevent){
		return "/news/keywords/?query=" + query + "&subevent=" + subevent + "&during=" + during + "&ts=" + end_ts;
	}
	this.weibo_ajax_url = function(query, end_ts, during, subevent, skip, limit, sort){
		var url = "/news/weibos/?query=" + query + "&limit=" + limit + "&skip=" + skip + "&ts=" + end_ts + "&during=" + during + "&subevent=" + subevent + "&sort=" + sort;
        return url
	}
    this.sub_weibo_ajax_url =  function(query){
        return "/news/sentiment/?query=" + query;
    }
    this.subevent_pie_ajax_url =  function(query){
        return "/news/subeventpie/?query=" + query;
    }
    this.sentiment_pie_ajax_url =  function(query){
        return "/news/sentimentpie/?query=" + query;
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
    this.select_subevent = "global"; // 当前选择的subevent, global表示总体，subeventid表示各子事件
    this.select_subevent_name = query;

    this.click_status = 'global'; // 标识当前的状态，global表示全局，peak表示点击了某个拐点后的情况
    var that = this;
    $("#clickalltime").click(function(){
        $("#cloudpie").css("display", "block");
        drawStatusTip(that.select_subevent_name, "全时段", null);
        that.drawTrendline();
        that.pullDrawPiedata();
        that.pullDrawClouddata();
        that.pullDrawWeibodata();
    });

    this.trend_count_obj = {
        "ts": [],
        "count": []
    };

    $("#sort_by_tfidf").click(function(){
        $("#sort_by_tfidf").css("color", "#333");
        $("#sort_by_total_weight").css("color", "-webkit-link");
        $("#sort_by_addweight").css("color", "-webkit-link");
        $("#sort_by_created_at").css("color", "-webkit-link");
        that.event_river_data['eventList'].sort(tfidf_comparator);
        drawSubeventTab(that.event_river_data, that); // 画子事件Tab
    });

    $("#sort_by_total_weight").click(function(){
        $("#sort_by_tfidf").css("color", "-webkit-link");
        $("#sort_by_total_weight").css("color", "#333");
        $("#sort_by_addweight").css("color", "-webkit-link");
        $("#sort_by_created_at").css("color", "-webkit-link");
        that.event_river_data['eventList'].sort(weight_comparator);
        drawSubeventTab(that.event_river_data, that); // 画子事件Tab
    });

    $("#sort_by_addweight").click(function(){
        $("#sort_by_tfidf").css("color", "-webkit-link");
        $("#sort_by_total_weight").css("color", "-webkit-link");
        $("#sort_by_addweight").css("color", "#333");
        $("#sort_by_created_at").css("color", "-webkit-link");
        that.event_river_data['eventList'].sort(addweight_comparator);
        drawSubeventTab(that.event_river_data, that); // 画子事件Tab
    });

    $("#sort_by_created_at").click(function(){
        $("#sort_by_tfidf").css("color", "-webkit-link");
        $("#sort_by_total_weight").css("color", "-webkit-link");
        $("#sort_by_addweight").css("color", "-webkit-link");
        $("#sort_by_created_at").css("color", "#333");
        that.event_river_data['eventList'].sort(createdat_comparator);
        drawSubeventTab(that.event_river_data, that); // 画子事件Tab
    });

    $("#sort_by_timestamp").click(function(){
        $("#sort_by_timestamp").css("color", "#333");
        $("#sort_by_weight").css("color", "-webkit-link");
        that.weibo_skip = 0;
        that.weibo_sort = 'timestamp';

        var ajax_url = that.weibo_ajax_url(that.query, that.end_ts, that.end_ts - that.start_ts, that.select_subevent, that.weibo_skip, that.weibo_limit_count, that.weibo_sort);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, Weibo_function);

        function Weibo_function(data){
            $("#weibo_ul").empty();
            that.weibo_skip += that.weibo_limit_count;
            refreshWeibodata(data);
        }
    });

    $("#sort_by_weight").click(function(){
        $("#sort_by_weight").css("color", "#333");
        $("#sort_by_timestamp").css("color", "-webkit-link");
        that.weibo_skip = 0;
        that.weibo_sort = 'weight';

        var ajax_url = that.weibo_ajax_url(that.query, that.end_ts, that.end_ts - that.start_ts, that.select_subevent, that.weibo_skip, that.weibo_limit_count, that.weibo_sort);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, Weibo_function);

        function Weibo_function(data){
            $("#weibo_ul").empty();
            that.weibo_skip += that.weibo_limit_count;
            refreshWeibodata(data);
        }
    });

    $("#more_information").click(function(){
        var ajax_url = that.weibo_ajax_url(that.query, that.end_ts, that.end_ts - that.start_ts, that.select_subevent, that.weibo_skip, that.weibo_limit_count, that.weibo_sort);

        that.call_sync_ajax_request(ajax_url, that.ajax_method, Weibo_function);

        function Weibo_function(data){
            if(data.length == 0){
                $("#more_information").html("加载完毕");
            }
            else{
                that.weibo_skip += that.weibo_limit_count;
                refreshWeibodata(data);
                $("#more_information").html("加载更多");
            }
        }
    });
}

function tfidf_comparator(a, b) {
    return parseFloat(b.tfidf) - parseFloat(a.tfidf);
}

function weight_comparator(a, b) {
    return parseInt(b.weight) - parseInt(a.weight);
}

function addweight_comparator(a, b) {
    return parseInt(b.addweight) - parseInt(a.addweight);
}

function createdat_comparator(a, b) {
    return parseInt(b.created_at) - parseInt(a.created_at);
}

// pull eventriver data
Opinion_timeline.prototype.pull_eventriver_data = function(){
	var that = this; //向下面的函数传递获取的值
	var ajax_url = this.eventriver_ajax_url(this.query, this.end_ts, this.end_ts - this.start_ts); //传入参数，获取请求的地址

	this.call_sync_ajax_request(ajax_url, this.ajax_method, Timeline_function); //发起ajax的请求
	
	function Timeline_function(data){    //数据的处理函数
        that.event_river_data = data;
        that.select_subevent = 'global'; // 默认处理总体
        // subevent_list = data['eventList'];
    }
}

// 
Opinion_timeline.prototype.drawFishbone = function(){
    drawFishbone(this.event_river_data);
}

function gweight_comparator(a,b){
    return parseInt(b.gweight) - parseInt(a.gweight);
}

function timestamp_comparator(a, b){
    return parseInt(a.news.timestamp) - parseInt(b.news.timestamp);
}

// 绘制鱼骨图
function drawFishbone(data){
    var html = '';
    data['eventList'].sort(timestamp_comparator);
    var eventListdata = data['eventList'];
    $(function(){
        $('#timeline1').b1njTimeline({
            'height' : eventListdata.length / 2 * 114
        });
    });
    for (var i=0; i < eventListdata.length; i++){
        var keyword = eventListdata[i]['name'];
        var news = eventListdata[i]['news'];
        var summary = news['content168'].substring(0, 100) + '...';;
        var datetime = news['datetime'];
        var title = news['title'];
        var source = news['transmit_name'];    
        html += "<li><time idx='" + i + "' " + "datetime='" + datetime + "'>" + datetime +"&nbsp;&nbsp;<span>"+keyword+"</span></time>";
        html += "<p><b>【" + title + "】:</b>" + summary + "</p>";
        html += "<span>转载于"+ source + "</span>&nbsp;&nbsp;<a target=\"_blank\" href=\"" + news["url"] + "\">新闻</a></li>";
    }
    $("#timeline1").append(html);
    $("#page").css("height", eventListdata.length / 2 * 114 + 150);
}

// 绘制子事件Tab
Opinion_timeline.prototype.drawSubeventsTab = function(){
    var that = this;
    this.event_river_data['eventList'].sort(tfidf_comparator);
    drawSubeventTab(this.event_river_data, that); // 画子事件Tab
}

// 绘制eventriver
Opinion_timeline.prototype.drawEventriver = function(){
    drawEventstack(this.event_river_data); // 主题河
}

// instance method, 获取数据并绘制趋势图
Opinion_timeline.prototype.drawTrendline = function(){
    this.trend_count_obj = {
        "ts":[],
        "count":[]
    };
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
	var ajax_url = this.pie_ajax_url(this.query, this.end_ts, this.end_ts - this.start_ts, this.select_subevent);
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
    this.weibo_skip = 0;
    this.weibo_sort = 'weight';
    $("#sort_by_weight").css("color", "#333");
    $("#sort_by_timestamp").css("color", "-webkit-link");
	var ajax_url = this.weibo_ajax_url(this.query, this.end_ts, this.end_ts - this.start_ts, this.select_subevent, this.weibo_skip, this.weibo_limit_count, this.weibo_sort);

	this.call_sync_ajax_request(ajax_url, this.ajax_method, Weibo_function);

    function Weibo_function(data){
        $("#weibo_ul").empty();
        that.weibo_skip += that.weibo_limit_count;
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
            drawStatusTip(that.select_subevent_name, '拐点' + title, click_ts);
            that.click_status = 'peak';
            that.weibo_skip = 0;
            var ajax_url = that.weibo_ajax_url(that.query, click_ts, that.pointInterval, that.select_subevent, that.weibo_skip, that.weibo_limit_count, that.weibo_sort);
            that.call_sync_ajax_request(ajax_url, that.ajax_method, Weibo_function);

            function Weibo_function(data){
                $("#weibo_ul").empty();
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


function drawEventstack(data){
	var x_data = data['dates'];
	var data = data['eventList'];
	var series_data = [];
	var series_name = [];
	var One_series_data = {};
	var temp_data = [];
	for (var k= 0; k < data.length; k++){
		One_series_value = [];
		One_series_time = [];
		temp_data = [];
		for(var i = 0; i < data[k]['evolution'].length; i++){
			One_series_value.push(data[k]['evolution'][i]['value']);
			temp_data.push(data[k]['evolution'][i]['value']);
			One_series_time.push(data[k]['evolution'][i]['time']);
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

		One_series_data = {'name':data[k]['name'], 'type':'line', 'smooth':true,'itemStyle':{'normal': {'areaStyle': {'type': 'default'}}},  'data':One_series_value};
		series_name.push(One_series_data['name']);
		series_data.push(One_series_data);
	}

    var selected_series_count = 10;
    if(selected_series_count > series_name.length){
        selected_series_count = series_name.length;
    }
    var selected_series_dict = {};
    for(var i = selected_series_count; i < series_name.length; i++){
        selected_series_dict[series_name[i]] = false;
    }

	option = {
	    tooltip : {
	        trigger: 'axis'
	    },
	    legend: {
	        data: series_name, 
            selected : selected_series_dict,
            selectedMode : "multiple"
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

    var option = {
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

function refreshSubeventPieData(data){
	var pie_data = [];
	var One_pie_data = {};
	for (var key in data){ 
		One_pie_data = {'value': data[key], 'name': key + (data[key]*100).toFixed(2)+"%"};
		pie_data.push(One_pie_data);		
	}

    var option = {
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
    var myChart = echarts.init(document.getElementById('subevent_pie'));
    myChart.setOption(option);
}
function refreshSentimentPieData(data){
	var pie_data = [];
	var One_pie_data = {};
	for (var key in data){ 
		One_pie_data = {'value': data[key], 'name': key + (data[key]*100).toFixed(2)+"%"};
		pie_data.push(One_pie_data);		
	}

    var option = {
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
    var myChart = echarts.init(document.getElementById('sentiment_pie'));
    myChart.setOption(option);
}
// 画tip
function drawStatusTip(subevent, peak_status, click_ts){
    if(click_ts != null){
        var dt = new Date(click_ts * 1000).format("yyyy年MM月dd日 hh:mm:ss");
        var time_block = peak_status + ' (' + dt + ')';
    }
    else{
        var time_block = peak_status;
    }
    $("#status_trend_tooltip").empty();
    $("#status_trend_tooltip").append('<span>当前点击了事件' + subevent + '&nbsp;&nbsp;时间: ' + time_block + '</span>');
    $("#status_cloudpie_tooltip").empty();
    $("#status_cloudpie_tooltip").append('<span>当前点击了事件' + subevent + '&nbsp;&nbsp;时间: ' + time_block + '</span>');
    $("#status_weibo_tooltip").empty();
    $("#status_weibo_tooltip").append('<span>当前点击了事件' + subevent + '&nbsp;&nbsp;时间: ' + time_block + '</span>');
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
    $("#subevent_tab").empty();
    var topic_weight = data['weight'];
    var data = data['eventList'];
    var html = '';
    html += '<div class="btn-group" id="global" name="' + query + '">';
    if(that.select_subevent == 'global'){
        html += '<button type="button" class="btn btn-success" style="margin: 5px;">' + query + '(' + topic_weight + ')</button>';
    }
    else{
        html += '<button type="button" class="btn btn-default" style="margin: 5px;">' + query + '(' + topic_weight + ')</button>';
    }
    html += '</div>';
    for (var i = 0;i < data.length;i++) {
        var name = data[i]['name'];
        var weight = data[i]['weight'];
        var addweight = data[i]['addweight'];
        var date = new Date(data[i]['created_at'] * 1000).format("yyyy-MM-dd hh:mm:ss");
        var tfidf = data[i]['tfidf'];
        var subeventid = data[i]['id'];
        html += '<div class="btn-group" id="' + subeventid + '" name="' + name + '">';
        if(that.select_subevent == subeventid){
            html += '<button type="button" class="btn btn-success" style="margin: 5px;">' + name + '(' + tfidf.toFixed(3) + ', ' + weight + ', ' + addweight  + ', ' + date  + ')</button>';
        }
        else{
            html += '<button type="button" class="btn btn-default" style="margin: 5px;">' + name + '(' + tfidf.toFixed(3) + ', ' + weight + ', ' + addweight  + ', ' + date  + ')</button>';
        }
        html += '</div>';
    }
    $("#subevent_tab").append(html);
    subevent_tab_click(that);
}

function subevent_tab_click(that){
    $div = $('#subevent_tab').children('div');
    $div.each(function(){
        $(this).click(function(){
            drawStatusTip($(this).text(), '全时段', null);
            var click_that = this;
            $('#subevent_tab').children('div').each(function(){
                if(click_that.id != this.id && $("#" + this.id + " :button").hasClass("btn btn-success")){
                    $("#" + this.id + " :button").removeClass("btn btn-success").addClass("btn btn-default");
                }
            });
            if($("#" + this.id + " :button").hasClass("btn btn-default")){
                $("#trendTimeline").css("display", "block");
                $("#cloudpie").css("display", "block");
                $("#news_rec").css("display", "block");
                $("#" + this.id + " :button").removeClass("btn btn-default").addClass("btn btn-success");
                var subevent_name = $("#" + this.id).attr("name");
                change_subevent_stat(this.id, subevent_name, that);
            }
            else{
                $("#" + this.id + " :button").removeClass("btn btn-success").addClass("btn btn-default");
                $("#trendTimeline").css("display", "none");
                $("#cloudpie").css("display", "none");
                $("#news_rec").css("display", "none");
            }
        })
    })
}

function change_subevent_stat(subeventid, subeventname, that){
    that.select_subevent = subeventid;
    that.select_subevent_name = subeventname;
    that.drawTrendline();
    that.pullDrawClouddata();
    that.pullDrawPiedata();
    that.pullDrawWeibodata();
}

// 画重要微博
function refreshWeibodata(data){  //需要传过来的是新闻的data
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
        var user_name;
        var source_from_name;
        if (d['transmit_name'] != null){
            user_name = d['transmit_name'];
        }
        else{
            user_name = d['user_name'];
        }
        if (d['source_from_name'] != null){
            source_from_name = d['source_from_name'];
        }
        else{
            source_from_name = d['user_name'];
        }
        var url;
        if (d["url"] != null){
            url = d["url"];
        }
        else{
            url = d["showurl"];
        }
        html += '<li class="item" style="width:1010px">';
        html += '<div class="weibo_detail" >';
        html += '<p>媒体:<a class="undlin" target="_blank" href="javascript;;">' + source_from_name + '</a>&nbsp;&nbsp;发布:';
        html += '<span class="title" style="color:#0000FF" id="' + d['_id'] + '"><b>[' + d['title'] + ']</b></span>';
        html += '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;<span id="content_summary_' + d['_id']  + '">' + content_summary + '</span>';
        html += '<span style="display: none;" id="content_' + d['_id']  + '">' + d['content168'] + '&nbsp;&nbsp;</span>';
        html += '</p>';
        html += '<div class="weibo_info">';
        html += '<div class="weibo_pz" style="margin-right:10px;">';
        html += '<span id="detail_' + d['_id'] + '"><a class="undlin" href="javascript:;" target="_blank" onclick="detail_text(\'' + d['_id'] + '\')";>阅读全文</a></span>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a class="undlin" href="javascript:;" target="_blank" onclick="open_same_list(\'' + d['_id'] + '\')";>相似新闻(' + same_text_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<a href="javascript:;" target="_blank">相关度(' + d['weight'] + ')</a>&nbsp;&nbsp;&nbsp;&nbsp;';
        html += '<a href="javascript:;" target="_blank" onclick="check_comments(\'' + d['_id'] + '\')">评论分析</a>&nbsp;&nbsp;&nbsp;&nbsp;';
        html += "</div>";
        html += '<div class="m">';
        html += '<a>' + new Date(d['timestamp'] * 1000).format("yyyy-MM-dd hh:mm:ss")  + '</a>&nbsp;-&nbsp;';
        html += '<a>转载于'+ user_name +'</a>&nbsp;&nbsp;';
        html += '<a target="_blank" href="'+ url +'">新闻</a>&nbsp;&nbsp;';
        html += '</div>';
        html += '</div>' 
        html += '</div>';
        html += '</li>';
        for (var i=0;i<same_text_count;i++){
            var dd = d['same_list'][i];
            var user_name;
            var source_from_name;
            if (dd['transmit_name'] != null){
                user_name = dd['transmit_name'];
            }
            else{
                user_name = dd['user_name'];
            }
            if (dd['source_from_name'] != null){
                source_from_name = dd['source_from_name'];
            }
            else{
                source_from_name = dd['user_name'];
            }
            var d_url;
            if (dd["url"] != null){
                d_url = dd["url"];
            }
            else{
                d_url = dd["showurl"];
            }
            html += '<div class="inner-same inner-same-' + d['_id'] + '" style="display:none;">';
            html += '<li class="item" style="width:1000px; border:2px solid">';
            html += '<div class="weibo_detail" >';
            html += '<p>媒体:<a class="undlin" target="_blank" href="javascript;;">' + source_from_name + '</a>&nbsp;&nbsp;发布:';
            html += '<span class="title" style="color:#0000FF" id="' + dd['_id'] + '"><b> ' + dd['title'] + ' </b></span>';
            html += '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;<span id="content_summary_' + d['_id']  + '">' + dd['content168'].substring(0, 168) + '...</span>';
            html += '<span style="display: none;" id="content_' + dd['_id']  + '">' + d['content168'] + '&nbsp;&nbsp;</span>';
            html += '</p>';
            html += '<div class="weibo_info">';
            html += '<div class="weibo_pz" style="margin-right:10px;">';
            html += '<span id="detail_' + dd['_id'] + '"><a class="undlin" href="javascript:;" target="_blank" onclick="detail_text(\'' + dd['_id'] + '\')";>阅读全文</a></span>&nbsp;|&nbsp;&nbsp;&nbsp;';
            html += '<a href="javascript:;" target="_blank">相关度(' + dd['weight'] + ')</a>&nbsp;&nbsp;&nbsp;&nbsp;';
            html += "</div>";
            html += '<div class="m">';
            html += '<a>' + new Date(dd['timestamp'] * 1000).format("yyyy-MM-dd hh:mm:ss")  + '</a>&nbsp;-&nbsp;';
            html += '<a>转载于'+ user_name +'</a>&nbsp;&nbsp;';
            html += '<a target="_blank" href="'+ d_url +'">新闻</a>&nbsp;&nbsp;';
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
function check_comments(text_id){
    // var text_id='1-1-30963839';
    var ajax_url = "/news/comments?query=" + query + "&news_id=" + text_id;
    $.ajax({
        url:ajax_url,
        type:"GET",
        dataType:"json",
        success:function(data){
            if (data["status"] == "success"){
                window.location.href="/comment?query=" + query + "&news_id=" + text_id;
            }
            else{
                alert("该新闻暂无评论");
            }
        }
    });
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


var query = QUERY;
var start_ts = START_TS;
var end_ts = END_TS;
var pointInterval = 3600 * 24;
var global_sub_weibos;
var opinion = new Opinion_timeline(query, start_ts, end_ts, pointInterval);
opinion.pull_eventriver_data();
opinion.drawEventriver();
opinion.drawFishbone();
opinion.call_sync_ajax_request(opinion.subevent_pie_ajax_url(this.query), opinion.ajax_method, refreshSubeventPieData);
opinion.call_sync_ajax_request(opinion.sentiment_pie_ajax_url(this.query), opinion.ajax_method, refreshSentimentPieData);
// opinion.pullDrawSubWeiboData();
// bindSentimentTabClick();
opinion.drawSubeventsTab();
opinion.drawTrendline();
opinion.pullDrawClouddata();
opinion.pullDrawWeibodata();
opinion.pullDrawPiedata();
