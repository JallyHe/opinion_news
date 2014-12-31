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

function Comment_opinion(query, start_ts, end_ts, cloud_div, pie_div, table_div, weibo_div,url){
	//传进来的参数，可以有
	this.query = query;
	this.start_ts = start_ts;
	this.end_ts = end_ts;
	this.ajax_method = "GET";
	this.minsize = 5;
	this.maxsize = 20;
	this.cloud_div = cloud_div ? cloud_div : '';
	this.pie_div = pie_div ? pie_div :'';
	this.table_div = table_div ? table_div :'';
	this.weibo_div = weibo_div ? weibo : '';
	this.ajax_url = url ? url : '';
}
//类中提供画饼图，关键词云图，关键微博，表格等等操作
Comment_opinion.prototype = {
	//控制传入的url和callback方法
	call_sync_ajax_request: function(url, method, callback){
        $.ajax({
            url: url,
            type: method,
            dataType: "json",
            async: false,
            success: callback
        })
    },

    comment_test: function(data){
    	console.log("123456789");
    	console.log(data);
    },
    //饼图
	Pie_function: function(data){
		console.log(data);
		var pie_data = [];
		var pie_div = this.pie_div; //此处div需要处理一下，把他转换成此处的id
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
	    var myChart = echarts.init(document.getElementById(pie_div));
	    myChart.setOption(option);
	},
	//关键词云
	Cloud_function: function(data){
		console.log(data);
	    var min_keywords_size = this.minsize;
	    var max_keywords_size = tis.maxsize;
	    var keywords_div_id = this.cloud_div;
	   	var color = '#11c897';
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
		        var size = this.defscale(count, min_count, max_count, min_keywords_size, max_keywords_size);
		        $('#'+keywords_div_id).append('<a><font style="color:' + color +  '; font-size:' + size + 'px;">' + keyword + '</font></a>');
		    }
		    on_load(keywords_div_id);
		}
	},
	//表格
	Table_function: function(data){
		console.log(data);
		
	},
	//微博
	Weibo_function: function(data){
		console.log(data);
		var weibo_div = this.weibo_div;
		$(weibo_div).empty();
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
	    $(weibo_div).append(html);
	    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
	},
	//通过词频来决定字体的大小
	defscale: function(count, mincount, maxcount, minsize, maxsize){
	    if(maxcount == mincount){
	        return (maxsize + minsize) * 1.0 / 2
	    }else{
	        return minsize + 1.0 * (maxsize - minsize) * Math.pow((count / (maxcount - mincount)), 2)
	    }
	},

}

var query = QUERY;
var start_ts = 1354896458;
var end_ts = 154686446564;
var cloud_url = "/news/keywords/?query=" + query;
Comment = new Comment_opinion(query, start_ts, end_ts);
Comment.call_sync_ajax_request(cloud_url, Comment.ajax_method, Comment.comment_test);