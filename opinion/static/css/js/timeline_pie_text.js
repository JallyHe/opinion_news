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
		return "/index/time/?topic=" + query;
	}
	this.pie_ajax_url = function(query, start_ts, end_ts){
		return "/index/ratio/?topic=" + query;
	}
	this.cloud_ajax_url = function(query, start_ts, end_ts){
		return "/index/keywords/?&topic=" + query;
	}
	this.weibo_ajax_url = function(query, start_ts, end_ts){
		return "/index/weibos/?&topic=" + query;
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
	console.log('timeline');
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Timeline_function); //发起ajax的请求
	
	function Timeline_function(data){    //数据的处理函数
		console.log(data);
		drawTab(data);
		event_river(data);
	} 
}

Opinion_timeline.prototype.pull_pie_data = function(){
	var that = this;
	var ajax_url = this.pie_ajax_url(this.query, this.start_ts, this.end_ts);
	console.log('pie');
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Pie_function);
	
	function Pie_function(data){    //数据的处理函数
		console.log(data);
		refreshPiedata(data);
	} 
}

Opinion_timeline.prototype.pull_cloud_data = function(){
	var that = this;
	var ajax_url = this.cloud_ajax_url(this.query, this.start_ts, this.end_ts);
	console.log('cloud');
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Cloud_function);

	function Cloud_function(data){    //数据的处理函数
	
		refreshDrawKeywords(that, data);
	} 
}

Opinion_timeline.prototype.pull_weibo_data = function(){
	var that = this;
	var ajax_url = this.weibo_ajax_url(this.query, this.start_ts, this.end_ts);
	console.log('weibo');
	this.call_sync_ajax_request(ajax_url, this.ajax_method, Weibo_function);

	function Weibo_function(data){    //数据的处理函数
		console.log(data);
		refreshWeibodata(data);
	} 
}
//事件流的展示
function event_river(data){
    option = {
	    title : {
	        text: 'Event River',
	        subtext: '纯属虚构'
	    },
	    tooltip : {
	        trigger: 'item',
	        enterable: true
	    },
	    legend: {
	        data:['财经事件', '政治事件']
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
	    series : [
	        {
	            "name": "财经事件", 
	            "type": "eventRiver", 
	            "weight": 123, 
	            "eventList": [
	                {
	                    "name": "阿里巴巴上市", 
	                    "weight": 123, 
	                    "evolution": [
	                        {
	                            "time": "2014-05-01", 
	                            "value": 14, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-02", 
	                            "value": 34, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-03", 
	                            "value": 60, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-04", 
	                            "value": 40, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-05", 
	                            "value": 10, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }
	                    ]
	                }, 
	                {
	                    "name": "阿里巴巴上市2", 
	                    "weight": 123, 
	                    "evolution": [
	                        {
	                            "time": "2014-05-02", 
	                            "value": 10, 
	                            "detail": {
	                                "link": "www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-03", 
	                            "value": 34, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-04", 
	                            "value": 40, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-05", 
	                            "value": 10, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }
	                    ]
	                }, 
	                {
	                    "name": "三星业绩暴跌", 
	                    "weight": 123, 
	                    "evolution": [
	                        {
	                            "time": "2014-05-03", 
	                            "value": 24, 
	                            "detail": {
	                                "link": "www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-04", 
	                            "value": 34, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-05", 
	                            "value": 50, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-06", 
	                            "value": 30, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-07", 
	                            "value": 20, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }
	                    ]
	                }
	            ]
	        }, 
	        {
	            "name": "政治事件", 
	            "type": "eventRiver", 
	            "weight": 123, 
	            "eventList": [
	                {
	                    "name": "Apec峰会", 
	                    "weight": 123, 
	                    "evolution": [
	                        {
	                            "time": "2014-05-06", 
	                            "value": 14, 
	                            "detail": {
	                                "link": "www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-07", 
	                            "value": 34, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-08", 
	                            "value": 60, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-09", 
	                            "value": 40, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-10", 
	                            "value": 20, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }
	                    ]
	                }, 
	                {
	                    "name": "运城官帮透视", 
	                    "weight": 123, 
	                    "evolution": [
	                        {
	                            "time": "2014-05-08", 
	                            "value": 4, 
	                            "detail": {
	                                "link": "www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-09", 
	                            "value": 14, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-10", 
	                            "value": 30, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-11", 
	                            "value": 20, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-12", 
	                            "value": 10, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }
	                    ]
	                }, 
	                {
	                    "name": "底层公务员收入超过副部长", 
	                    "weight": 123, 
	                    "evolution": [
	                        {
	                            "time": "2014-05-11", 
	                            "value": 4, 
	                            "detail": {
	                                "link": "www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-12", 
	                            "value": 24, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-13", 
	                            "value": 40, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-14", 
	                            "value": 20, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-15", 
	                            "value": 15, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }, 
	                        {
	                            "time": "2014-05-16", 
	                            "value": 10, 
	                            "detail": {
	                                "link": "http://www.baidu.com", 
	                                "text": "百度指数", 
	                                "img": '../asset/ico/favicon.png'
	                            }
	                        }
	                    ]
	                }
	            ]
	        }
	    ]
	};
    var myChart = echarts.init(document.getElementById('event_river'));
    myChart.setOption(option);       
}

function refreshPiedata(data){
	console.log(data);
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
function drawTab(data){
	var result = [];
	var result1 = [];
	var result2 = [];            		
	var html = "<tbody>";
    for (var i = 0;i < data.length;i++) {
        result[i] = data[i][1]; //开始时间
        result1[i] = data[i][2];  //结束时间                 
        var s = i.toString();
        result2[i] = data[i][0]; 
        if ((i+1)%5 == 1){
        	html+='<tr><td style ="padding:5px;padding-left:10px;width:180px;height:20px;font-size:14px;"><input type="checkbox" value = '+ s +' name="c_topic">'+result2[i]+'</td>';
        }	
        else if ((i+1)%5 == 0){
        	html+='<td style ="padding:5px;width:180px;height:20px;font-size:14px;"><input type="checkbox" value = '+ s +' name="c_topic">'+result2[i]+'</td></tr>';
        }
        else{
        	html+='<td style ="padding:5px;width:180px;height:20px;font-size:14px;"><input type="checkbox" value = '+ s +' name="c_topic">'+result2[i]+'</td>';
        }       
    }
    html+='</tbody>';
    $("#checkbox").append(html);
}

function refreshWeibodata(data){  //需要传过来的是新闻的data
    $("#vertical-ticker").empty();
	var html = "";
	for(var i = 0; i < data.length; i += 1){
		var da = data[i][1];
		var c_topic = da['c_topic'];
		var mid = da['_id'];
		var user = da['user'];
		var title = da['title'];
		var content = da['content'];
		if (content.length>200){
			new_content = ''
			for(var j=0; j<200; j+=1){
				new_content += content[j];
			}
			new_content +=  '...';
		}
		var time = da['time'];
		var new_data = new Date(time * 1000).format("yyyy年MM月dd日 hh:mm:ss")
		var source = da['source'];
		html += '<div class="inner">';
		html += '<span class="title" style="color:#0000FF"><b>'+ mid +':'+ c_topic + '</b></span><br>';
		html += '<span class="title" style="color:#0000FF"><b>'+ title + '</b></span><br/>';
		html += '<span>'+ new_content+ '</span><br>'; 
		html += '<span style="float:right;">'+new_data + user +"发布于"+source;                      
		html +='</div>';
	}
	$("#vertical-ticker").append(html);
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

var query = '两会';
var start_ts = 1354896458;
var end_ts = 154686446564;
Timeline = new Opinion_timeline(query, start_ts, end_ts);
Timeline.pull_cloud_data();
Timeline.pull_weibo_data();
Timeline.pull_pie_data();
Timeline.pull_timeline_data();