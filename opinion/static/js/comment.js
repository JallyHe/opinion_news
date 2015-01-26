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

	//tab
	Tab_fuiction: function(data){
		var html = '';
		//var tab_div = this.tab_div;
		var n = data.length;
		var tab_wid = 100.0/n + '%';
		topic_son = data[0][0];
		var topic = [];
        for (var i = 0;i < data.length;i++) {
	        topic[i] = data[i][0]; 
	        var s = i.toString();
	        if(i==0){
	            html += '<a style="display: block;width:'+tab_wid+'" topic='+ topic[i] + ' name="c_topic" class="tabLi gColor0 curr" href="javascript:;" >';
	            html += '<div class="nmTab">'+ topic[i]+ '</div>';
	            html += '<div class="hvTab">'+topic[i]+'</div></a>';
	        }
	        else{
	            html += '<a style="display: block;width:'+tab_wid+'" topic='+ topic[i] + ' name="c_topic" class="tabLi gColor0" href="javascript:;" >';
	            html += '<div class="nmTab">'+ topic[i]+ '</div>';
	            html += '<div class="hvTab">'+topic[i]+'</div></a>';
	        }
	    };
	    $(tab_div).append(html);
	},

	//表格
	Table_function: function(data){
		var that = this;
        var topic_child_keywords = data;

        var m = 0;
        var html = '';
        for (var topic in topic_child_keywords){
            m++;
            if( m > 10) {
                break;
            }
            html += '<tr topic=' + topic_child_keywords[topic][0] + '>'; 
            html += "<td><b>"+m+"</b></td><td><b onclick = \"connect('"+topic+"')\" style =\"width:20px;cursor:pointer;\">"+topic_child_keywords[topic][0]+"</b></td>";
            var child_keywords = topic_child_keywords[topic][1];
            if (child_keywords.length >= 10){
                total = 10;
            }
            else{
                total = child_keywords.length;
            }
            for (var n = 0 ;n < total; n++){
                html += '<td>' + child_keywords[n] + '</td>'
            }
            html += "</tr>";
        }
        $("#alternatecolor").append(html);

        var target_html = '';
        for (var topic in topic_child_keywords){
            target_html += '<tr style="height:25px">';                    
            target_html += '<td><b>'+topic_child_keywords[topic][0]+'</b></td>';
            var child_keywords = topic_child_keywords[topic][1];
            if (child_keywords.length>=100){
            	total = 100;
            }
            else{
            	total = child_keywords.length;
            }
            for (var n = 0 ;n < total; n++){
                target_html += '<td>'+ child_keywords[n] + '</td>'
            }
            target_html += "</tr>";
        }
        $("#alternate").append(target_html);
    },

	Tab_click_function: function(){ 
		var that = this; 
		$("#Tableselect").children("a").unbind();
        $("#Tableselect").children("a").click(function(){
            var select_a = $(this);
            var unselect_a = $(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                topic_son = select_a.attr('topic');          
                that.Weibo_function(weibo_data);
             }
         });
    },

	//微博
	Weibo_function: function(data){
		weibo_data = data;
		var data = data[topic_son];
		var html = '';
		$(weibo_div).empty();      
        html += '<div class="tang-scrollpanel-wrapper">';
        html += '<div class="tang-scrollpanel-content">';
        html += '<ul id="weibo_ul">';
        for(var i = 0; i < data.length; i += 1){
	        var da = data[i];
	        var uid = da['user'];
	        var name;
	        if ('name' in da){
	            name = da['name'];
	            if(name == 'unknown'){
	                name = '未知';
	            }
	        }
	        else{
	            name = '未知';
	        }
	        var mid = da['_id'];
	        var retweeted_mid = da['retweeted_mid'];
			var retweeted_uid = da['retweeted_uid'];
	        var text = da['text'];
	        if (da['geo']){
				var ip = da['geo'];
				var loc = ip;
			}
			else{
				var loc = ip = '未知';
			}
	        var reposts_count = da['reposts_count'];
	        var comments_count = da['comments_count'];
	        var timestamp = da['time'];
	        var date = new Date(timestamp * 1000).format("yyyy年MM月dd日 hh:mm:ss");
	        var user_link = 'http://weibo.com/u/' + uid;
	        var weibo_link = da['weibo_link'];
			var repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + mid;
			var user_image_link = '/static/img/unknown_profile_image.gif';
			/*var user_image_link = da['profile_image_url'];
			if (user_image_link == ''){
				user_image_link = '/static/img/unknown_profile_image.gif';
			}*/
	        html += '<li class="item"><div class="weibo_face"><a target="_blank" href="' + user_link + '">';
	        html += '<img src="' + user_image_link + '">';
			html += '</a></div>';
			html += '<div class="weibo_detail">';
			html += '<p>昵称:<a class="undlin" target="_blank" href="' + user_link  + '">' + name + '</a>(' + loc + ')&nbsp;&nbsp;发布ip:' + '未知' + '&nbsp;&nbsp;发布内容：&nbsp;&nbsp;' + text + '</p>';;
			html += '<div class="weibo_info">';
			html += '<div class="weibo_pz">';
			html += '<a class="undlin" href="javascript:;" target="_blank">转发数(' + reposts_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
			html += '<a class="undlin" href="javascript:;" target="_blank">评论数(' + comments_count + ')</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
			html += '<a class="undlin" href="javascript:;" target="_blank">粉丝数(未知)</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
			html += '<a class="undlin" href="javascript:;" target="_blank">关注数(未知)</a>&nbsp;&nbsp;|&nbsp;&nbsp;';
			html += '<a class="undlin" href="javascript:;" target="_blank">微博数(未知)</a></div>';
			html += '<div class="m">';
			html += '<a class="undlin" target="_blank" href="' + weibo_link + '">' + date + '</a>&nbsp;-&nbsp;';
			html += '<a target="_blank" href="' + weibo_link + '">微博</a>&nbsp;-&nbsp;';
			html += '<a target="_blank" href="' + user_link + '">用户</a>&nbsp;-&nbsp;';
			html += '<a target="_blank" href="' + '#huaxiang' + '">画像</a>&nbsp;-&nbsp;';
			html += '<a target="_blank" href="' + repost_tree_link + '">转发树</a>';
			if(retweeted_mid != '0'){
    			var source_repost_tree_link = 'http://219.224.135.60:8080/show_graph/' + retweeted_mid;
    			html += '&nbsp;-&nbsp;<a target="_blank" href="' + source_repost_tree_link + '">转发子树</a>';
			}
	        html += '</div>';
	        html += '</div>';
	        html += '</div>';
	        html += '</li>';
   		}
	    html += '</ul>';
	    html += '</div>';
	    $(weibo_div).append(html);
	    $("#weibos_div").css("height", $(weibo_div).css("height"));
	},

	//新闻
	News_function: function(data){
        global_comments_data = data;
        var select_sentiment = 1;
        refreshDrawComments(data, select_sentiment);
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

function refreshDrawCommentsOpinion(data){
    var news_div = "#vertical-ticker_opinion";
    $(news_div).empty();

    var sentiment_dict = {
        0: '无倾向',
        1: '高兴',
        2: '愤怒',
        3: '悲伤'
    }

    var html = "";
    var da = data[1];
    for ( e in da){
        var d = da[e];
        var content_summary = d['content168'];
        var user_img_link = '/static/img/unknown_profile_image.gif';
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
        html += '<span><a class="undlin" href="javascript:;" target="_blank">相关度(' + d['weight'].toFixed(3) + ')</a></span>&nbsp;&nbsp;';
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
    $(news_div).append(html);
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

function refreshDrawComments(data, select_sentiment){
    var news_div = "#vertical-ticker";
    $(news_div).empty();

    var sentiment_dict = {
        0: '无倾向',
        1: '高兴',
        2: '愤怒',
        3: '悲伤'
    }

    var html = "";
    data[select_sentiment].sort(gweight_comparator);
    var da = data[select_sentiment];
    for ( e in da){
        var d = da[e];
        var content_summary = d['content168'];
        var user_img_link = '/static/img/unknown_profile_image.gif';
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
        html += '<span><a class="undlin" href="javascript:;" target="_blank">相关度(' + d['gweight'].toFixed(3) + ')</a></span>&nbsp;&nbsp;';
        html += "</div>";
        html += '<div class="m">';
        html += '<a class="undlin" target="_blank" >' + new Date(d['timestamp'] * 1000).format("yyyy-MM-dd hh:mm:ss")  + '</a>&nbsp;-&nbsp;';
        html += '<a target="_blank">发表于'+ d["comment_source"] +'</a>&nbsp;&nbsp;';
        html += '</div>';
        html += '</div>' 
        html += '</div>';
        html += '</li>';
    }
    $(news_div).append(html);
    $("#content_control_height").css("height", $("#weibo_ul").css("height"));
}

function bindOpinionTabClick(that){
    var select_div_id = "OpinionTabDiv";
    var sentiment_map = {
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
            var select_clusterid = select_a.attr('clusterid');
            refreshDrawCommentsOpinion(global_comments_opinion[select_clusterid]);
        }
    });
}

function bindSentimentTabClick(that){
    var select_div_id = "SentimentTabDiv";
    var sentiment_map = {
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
            refreshDrawComments(global_comments_data, select_sentiment);
        }
    });
}

function connect(data){
	topic_son = data;
    $("#alternatecolor tr").each(function() {
        var select_all =$(this);
        if(select_all.attr('topic') == data){
            if(!select_all.hasClass("tablecurrent")){
                select_all.addClass("tablecurrent");
            }
        }
        else{
            if(select_all.hasClass("tablecurrent")){
                select_all.removeClass('tablecurrent');
            }
        }

    })
   refreshWeiboTab(data);
}

function refreshWeiboTab(data){
    var curr_data = data;
     $("#Tableselect a").each(function() {
        var select_a = $(this);
        var select_a_sentiment = select_a.attr('topic');
        if (select_a_sentiment == curr_data){
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
            }
        }
        else{
            if(select_a.hasClass('curr')) {
                select_a.removeClass('curr');
            }
        }
    });
    Comment.Weibo_function(weibo_data);
}

var query = QUERY;
var news_id = NEWS_ID;
var start_ts = undefined;
var end_ts = undefined;
var pie_url = "/comment/ratio/?query=" + query + "&news_id=" + news_id;
var keywords_url = "/comment/keywords/?query=" + query + "&news_id=" + news_id;
var sentiment_url = "/comment/sentiment/?query=" + query + "&news_id=" + news_id;
var cluster_url = "/comment/cluster/?query=" + query + "&news_id=" + news_id;

comment = new Comment_opinion(query, start_ts, end_ts);
comment.call_sync_ajax_request(pie_url, comment.ajax_method, comment.Pie_function);
comment.call_sync_ajax_request(keywords_url, comment.ajax_method, comment.Table_function);
comment.call_sync_ajax_request(sentiment_url, comment.ajax_method, comment.News_function);
bindSentimentTabClick(comment);
comment.call_sync_ajax_request(cluster_url, comment.ajax_method, comment.Cluster_function);
bindOpinionTabClick(comment);

