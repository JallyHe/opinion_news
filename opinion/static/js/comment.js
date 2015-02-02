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

var global_comments_data = undefined;
var global_comments_opinion = undefined;
var global_subevent_display = 10;
var global_senti_display = 10;
var addition = 10;

function Comment_opinion(query, start_ts, end_ts){
	//传进来的参数，可以有
	this.query = query;
	this.start_ts = start_ts;
	this.end_ts = end_ts;
	this.ajax_method = "GET";
	this.minsize = 5;
	this.maxsize = 20;
    this.news_div = "vertical-ticker";
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

    Cluster_function: function(data){
        global_comments_opinion = data;

        var select_data;
        var select_tab;
        for(var k in data){
            select_tab = k;
            select_data = data[k];
            break;
        }

        var tabs_list = [];
        for(var k in data){
            tabs_list.push([k, data[k][0]]);
        }

        refreshDrawOpinionTab(tabs_list, select_tab);
        refreshDrawCommentsOpinion(select_data);
    },

    //饼图
	Pie_function: function(data){
        var pie_div = "main";
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
	    var myChart = echarts.init(document.getElementById(pie_div));
	    myChart.setOption(option);
	},
    //情绪饼图
	SentiPie_function: function(data){
        var pie_div = "senti_pie";
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
	    var myChart = echarts.init(document.getElementById(pie_div));
	    myChart.setOption(option);
	},

	//新闻
	News_function: function(data){
        global_comments_data = data;
        var select_sentiment = 1;
        refreshDrawComments(data, select_sentiment);
	},

}

function refreshDrawOpinionTab(tabs_list, select_tab){
    $("#OpinionTabDiv").empty();
    var html = '';
    for(var i=0; i < tabs_list.length; i++){
        var clusterid = tabs_list[i][0];
        var words = tabs_list[i][1];
        if(select_tab == clusterid){
            html += '<a clusterid="' + clusterid + '" class="tabLi gColor1 curr" href="javascript:;" style="display: block;">';
        }
        else{
            html += '<a clusterid="' + clusterid + '" class="tabLi gColor1" href="javascript:;" style="display: block;">';
        }
        html += '<div class="nmTab">' + words  + '</div>';
        html += '<div class="hvTab">' + words + '</div>';
        html += '</a>';
    }
    $("#OpinionTabDiv").append(html);
}

function gweight_comparator(a, b){
    return parseInt(b.gweight) - parseInt(a.gweight);
}
function weight_comparator(a, b){
    return parseInt(b.weight) - parseInt(a.weight);
}

function refreshDrawCommentsOpinion(data){
    var news_div = "#vertical-ticker_opinion";
    $(news_div).empty();

    var counter = 0;
    var html = "";
    if (data){
        var da = data[1];
    }
    else{
        var da = {};
    }
    for (var e in da){
        if (counter == global_subevent_display){
            break;
        }
        counter += 1;
        var d = da[e];
        var content_summary = d['content168'];
        var user_img_link = '/static/img/unknown_profile_image.gif';
        var weight;
        if ('weight' in d){
            weight = d['weight'];
        }
        else if('gweight' in d){
            weight = d['gweight'];
        }
        else{
            weight = 0;
        }
        html += '<li class="item" style="width:1010px">';
        html += '<div class="weibo_face"><a target="_blank" href="#">';
        html += '<img src="' + user_img_link + '">';
        html += '</a></div>';
        html += '<div class="weibo_detail" >';
        html += '<p>用户:<a class="undlin" target="_blank" href="' + d["user_comment_url"] + '">' + d['user_name'] + '</a>&nbsp;&nbsp;';
        html += '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;<span id="content_summary_' + d['_id']  + '">' + content_summary + '</span>';
        html += '</p>';
        html += '<div class="weibo_info">';
        html += '<div class="weibo_pz" style="margin-right:10px;">';
        html += '<span><a class="undlin" href="javascript:;" target="_blank">赞数(' + d['attitudes_count'] + ')</a></span>&nbsp;&nbsp;|&nbsp;&nbsp;';
        html += '<span><a class="undlin" href="javascript:;" target="_blank">相关度(' + weight.toFixed(3) + ')</a></span>&nbsp;&nbsp;';
        //html += '<span><a class="undlin" href="javascript:;" target="_blank">情绪(' + sentiment_dict[d['sentiment']] + ')</a></span>&nbsp;&nbsp;';
        html += "</div>";
        html += '<div class="m">';
        html += '<a class="undlin" target="_blank" >' + new Date(d['timestamp'] * 1000).format("yyyy-MM-dd hh:mm:ss")  + '</a>&nbsp;-&nbsp;';
        html += '<a target="_blank">发表于'+ d["comment_source"] +'</a>&nbsp;&nbsp;';
        html += '</div>';
        html += '</div>' 
        html += '</div>';
        html += '</li>';
    }

    if (counter < global_subevent_display){
        $("#subevent_more_information").html("加载完毕");
    }
    $(news_div).append(html);
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

function refreshDrawComments(data, select_sentiment){
    var news_div = "#vertical-ticker";
    $(news_div).empty();

    var sentiment_dict = {
        0: '中性',
        1: '高兴',
        2: '愤怒',
        3: '悲伤'
    }

    var counter = 0;
    var html = "";

    if (select_sentiment in data){
        data[select_sentiment].sort(gweight_comparator);
        var da = data[select_sentiment];
    }
    else{
        var da = [];
    }

    for (var e in da){
        if (counter == global_senti_display){
            break;
        }
        counter += 1;
        var d = da[e];
        var content_summary = d['content168'];
        var user_img_link = '/static/img/unknown_profile_image.gif';
        var weight;
        if ('weight' in d){
            weight = d['weight'];
        }
        else if('gweight' in d){
            weight = d['gweight'];
        }
        else{
            weight = 0;
        }
        html += '<li class="item" style="width:1010px">';
        html += '<div class="weibo_face"><a target="_blank" href="#">';
        html += '<img src="' + user_img_link + '">';
        html += '</a></div>';
        html += '<div class="weibo_detail" >';
        html += '<p>用户:<a class="undlin" target="_blank" href="' + d["user_comment_url"] + '">' + d['user_name'] + '</a>&nbsp;&nbsp;';
        html += '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;<span id="content_summary_' + d['_id']  + '">' + content_summary + '</span>';
        html += '</p>';
        html += '<div class="weibo_info">';
        html += '<div class="weibo_pz" style="margin-right:10px;">';
        html += '<span><a class="undlin" href="javascript:;" target="_blank">赞数(' + d['attitudes_count'] + ')</a></span>&nbsp;&nbsp;';
        html += '<span><a class="undlin" href="javascript:;" target="_blank">相关度(' + weight.toFixed(3) + ')</a></span>&nbsp;&nbsp;';
        html += "</div>";
        html += '<div class="m">';
        html += '<a class="undlin" target="_blank" >' + new Date(d['timestamp'] * 1000).format("yyyy-MM-dd hh:mm:ss")  + '</a>&nbsp;-&nbsp;';
        html += '<a target="_blank">发表于'+ d["comment_source"] +'</a>&nbsp;&nbsp;';
        html += '</div>';
        html += '</div>' 
        html += '</div>';
        html += '</li>';
    }

    if (counter < global_senti_display){
        $("#senti_more_information").html("加载完毕");
    }

    $(news_div).append(html);
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

function bindOpinionTabClick(that){
    var select_div_id = "OpinionTabDiv";
    $("#"+select_div_id).children("a").unbind();
    $("#"+select_div_id).children("a").click(function() {
        var select_a = $(this);
        var unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
            var select_clusterid = select_a.attr('clusterid');
            global_subevent_display = 10;
            $("#subevent_more_information").html("加载更多");
            refreshDrawCommentsOpinion(global_comments_opinion[select_clusterid]);
        }
    });
}

function bindSentimentTabClick(that){
    var select_div_id = "SentimentTabDiv";
    var sentiment_map = {
        'neutral': 0,
        'happy': 1,
        'angry': 2,
        'sad': 3
    }
    $("#"+select_div_id).children("a").unbind();
    $("#"+select_div_id).children("a").click(function() {
        var select_a = $(this);
        var unselect_a = $(this).siblings('a');
        if(!select_a.hasClass('curr')) {
            select_a.addClass('curr');
            unselect_a.removeClass('curr');
            var select_sentiment = sentiment_map[select_a.attr('sentiment')];
            global_senti_display = 10;
            $("#senti_more_information").html("加载更多");
            refreshDrawComments(global_comments_data, select_sentiment);
        }
    });
}

function bindSentiMoreClick(){
    $("#senti_more_information").click(function(){
        global_senti_display += addition;
        var select_div_id = "SentimentTabDiv";
        var sentiment_map = {
            'neutral': 0,
            'happy': 1,
            'angry': 2,
            'sad': 3
        }
        $("#"+select_div_id).children("a").each(function() {
            if($(this).hasClass('curr')) {
                var select_a = $(this);
                var select_sentiment = sentiment_map[select_a.attr('sentiment')];
                refreshDrawComments(global_comments_data, select_sentiment);
                return false;
            }
        });
    });
}

function bindSubeventMoreClick(){
    $("#subevent_more_information").click(function(){
        global_subevent_display += addition;
        var select_div_id = "OpinionTabDiv";
        $("#"+select_div_id).children("a").each(function() {
            if($(this).hasClass('curr')) {
                var select_a = $(this);
                var select_clusterid = select_a.attr('clusterid');
                refreshDrawCommentsOpinion(global_comments_opinion[select_clusterid]);
                return false;
            }
        });
    });
}


var query = QUERY;
var news_id = NEWS_ID;
var start_ts = undefined;
var end_ts = undefined;
var pie_url = "/comment/ratio/?query=" + query + "&news_id=" + news_id;
var senti_pie_url = "/comment/sentiratio/?query=" + query + "&news_id=" + news_id;
// var keywords_url = "/comment/keywords/?query=" + query + "&news_id=" + news_id;
var sentiment_url = "/comment/sentiment/?query=" + query + "&news_id=" + news_id;
var cluster_url = "/comment/cluster/?query=" + query + "&news_id=" + news_id;

comment = new Comment_opinion(query, start_ts, end_ts);
comment.call_sync_ajax_request(pie_url, comment.ajax_method, comment.Pie_function);
comment.call_sync_ajax_request(senti_pie_url, comment.ajax_method, comment.SentiPie_function);
// comment.call_sync_ajax_request(keywords_url, comment.ajax_method, comment.Table_function);
comment.call_sync_ajax_request(sentiment_url, comment.ajax_method, comment.News_function);
bindSentiMoreClick();
bindSentimentTabClick(comment);
comment.call_sync_ajax_request(cluster_url, comment.ajax_method, comment.Cluster_function);
bindOpinionTabClick(comment);
bindSubeventMoreClick();

