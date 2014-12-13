
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
        if(/(y+)/.test(format)) 
        format=format.replace(RegExp.$1, (this.getFullYear()+"").substr(4 - RegExp.$1.length)); 
        for(var k in o)
        if(new RegExp("("+ k +")").test(format)) 
            format = format.replace(RegExp.$1, RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length)); 
        return format; 
    }

    var timeline;
        var data;
        // Called when the Visualization API is loaded.
        $(document).ready(function(){   //网页加载时执行下面函数
        var style = '0';
        gettimeline_data();
        getweibos_data();
        event_river();
   })
        var result = [];
        var result1 = [];
        var result2 = [];

function event_river(){
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

    function gettimeline_data() {
        var topic = '两会';
        var html ="";
        $.ajax({
            url: "/index/time/?topic=" + topic,
            type: "GET",
            dataType:"json",
            async: false,
            success: function(data){
            		var html = "<tbody>";
                for (var i = 0;i < data.length;i++) {
                    result[i] = data[i][1];
                    result1[i] = data[i][2];                   
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
                    
                    
                };
                html+='</tbody>';
                $("#checkbox").append(html);
               


               // drawVisualization(); 
               getkeywords_data();
               bindinput_tab(); 
            }       
        });
    }
    function bindinput_tab(){
        var style;
        var k = 0;
        $("#checkbox span").children("input").unbind();
        $("#checkbox span").children("input").click(function() { 
            var select_input = $(this);
            style = select_input.attr('value');
            if(!select_input.hasClass("input_curr")){
                select_input.addClass("input_curr");
                unbind_tab(k); 
                var i = Number(style);
                // var html = '';
                // html += '<a value='+ style + ' class="tabLi gColor0 curr" href="javascript:;" style="display: block;">';
                // html += '<div class="nmTab">'+ result2[i]+ '</div>';
                // html += '<div class="hvTab">'+result2[i]+'</div></a>';
                // $("#Tableselect").append(html);
                getweibos_data(style);
                k++;

            }
            else {
                select_input.removeClass("input_curr");
                k--;
                removeElement(style,k);
            } 
            bindSentimentTabClick();     
        })
    }    
    function unbind_tab(k){
        var time = k;
        if(k>=1){
          $("#Tableselect").children("a").each(function(){
            var select= $(this);
            select.removeClass("curr");
          })  
        }

    }

    function removeElement(data,k){
        var el = document.getElementById("Tableselect");
        var first;
        var time;
        time =k;
        console.log(time);
        $("#Tableselect").children("a").each(function(){
            var obj = $(this);
            var obj_a = this;
            if(obj.attr('value') == data){
                el.removeChild(obj_a);
               if(obj.hasClass("curr")){
                    obj.removeClass("curr");
                    
                    $("#vertical-ticker").empty();

                    first = $("#Tableselect").children("a").first();
                    console.log(first);
                    first.addClass("curr");
                    console.log('abx');
                    var style = first.attr("value");
                    if(time >0){
                        getweibos_data(style);
                    }
                    
                    //document.getElementById('vertical-ticker').innerHtml = "";
               }
                  
               
            }
        })
    }
    
    function bindSentimentTabClick(){

        
        $("#Tablebselect").children("a").unbind();

        $("#Tableselect").children("a").click(function() {
            var select_a = $(this);
            var unselect_a = $(this).siblings('a');
            if(!select_a.hasClass('curr')) {
                select_a.addClass('curr');
                unselect_a.removeClass('curr');
                style = select_a.attr('value');
              
                getweibos_data(style);

            }
        });
    }


        function drawVisualization() {
            var data = [];
            var data_start = [];
            var data_end = [];
            for (var i =0 ; i< result.length; i++){
                data_end[i] = new Date(parseInt(result1[i]) * 1000);
                data_start[i] = new Date(parseInt(result[i]) * 1000);
                data[i] = {'start':data_start[i],'end':data_end[i],'content':result2[i]};
            }
						var height_str = 25*result2.length;//需寻找一种机制让时间轴的高度动态可调
						height_str += 'px';       

            // specify options
            var options = {
                'width':  '100%',
                'height': height_str,
                'editable': true,   // enable dragging and editing events
                'style': 'box'
            };

            // Instantiate our timeline object.
            timeline = new links.Timeline(document.getElementById('mytimeline'));
            // Draw our timeline with the created data and options
            timeline.draw(data, options);
        }
    var query = "中国";
    var ts = 1378035900;
    var START_TS = 1377965700
    var during = ts-START_TS;
    var result3 = [];


    $(document).ready(function(){   //网页加载时执行下面函数
       getpie_data();
       getcloud_data();
   })

    function getcloud_data() {
        var topic = '两会';
        $.ajax({
            url: "/index/keywords/?topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
                console.log(data);
                draw_cloud(data);
            }
        });      
    }

    function draw_cloud(data){
  var div_id_cloud = 'keywords_cloud_div';
  var max_keywords_size = 20;
  var min_keywords_size = 5;
  var value = [];
  var key = [];
  if (data=={}){
    $('#'+div_id_cloud).append("<a style='font-size:1ex'>关键词云数据为空</a>");
  }
  else{
    var min_count, max_count = 0, words_count_obj = {};
    for(var k in data){
        value.push(data[k]);
    }
    console.log(value);
    for (var i=0;i<value[0].length; i++){
      var word = value[0][i][1];
      var count = value[0][i][0];
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


    // console.log(words_count_obj);
    var color = '#11c897';
    for(var keyword in words_count_obj){
        var count = words_count_obj[keyword];
        var size = defscale(count, min_count, max_count, min_keywords_size, max_keywords_size);
        $('#'+div_id_cloud).append('<a><font style="color:' + color +  '; font-size:' + size + 'px;">' + keyword + '</font></a>');
    }
    console.log(div_id_cloud);
    on_load(div_id_cloud);
 

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


    function getpie_data() {
        var result = [];
        var topic = '两会';
        $.ajax({
            url: "/index/ratio/?topic=" + topic,
            type: "GET",
            dataType:"json",
            async:false,
            success: function(data){
            	for (var i =0 ; i< result2.length; i++){
            		result3[i] = data[result2[i]]
            }

                on_update(result);
                draw_pie(data);
            }
        });
       
    }

    function on_update(result) {
        var percentage = []; 
        percentage[0] = (result3[0]*100).toFixed(2)+"%";
        percentage[1] = (result3[1]*100).toFixed(2)+"%";
        percentage[2] = (result3[2]*100).toFixed(2)+"%";
        percentage[3] = (result3[3]*100).toFixed(2)+"%";
        percentage[4] = (result3[4]*100).toFixed(2)+"%";
        percentage[5] = (result3[5]*100).toFixed(2)+"%";
        percentage[6] = (result3[6]*100).toFixed(2)+"%";
        percentage[7] = (result3[7]*100).toFixed(2)+"%";
        percentage[8] = (result3[8]*100).toFixed(2)+"%";
        percentage[9] = (result3[9]*100).toFixed(2)+"%";
        percentage[10] = (result3[10]*100).toFixed(2)+"%";
 

      var pie_data=[];
        pie_data = [{value:  result3[0], name:result2[0]+percentage[0]}, {value: result3[1], name:result2[1]+percentage[1]}, 
        {value:  result3[2], name:result2[2]+percentage[2]}, {value: result3[3], name:result2[3]+percentage[3]},
         {value:  result3[4], name:result2[4]+percentage[4]},{value:  result3[5], name:result2[5]+percentage[5]},{value:  result[6], name:result2[6]+percentage[6]}
         ,{value:  result3[7], name:result2[7]+percentage[7]},{value:  result3[8], name:result2[8]+percentage[8]},{value:  result3[9], name:result2[9]+percentage[9]},
         {value:  result3[10], name:result2[10]+percentage[10]}];
    
    option = {
        title : {
            text: '',
            x:'center',
            textStyle:{
            fontWeight:'lighter',
            fontSize: 13,
            }        
        },
        // tooltip : {
        //     trigger: 'item',
        //     formatter: "{a} <br/>{b} : {c} ({d}%)"
        // },
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

    function draw_pie(result) {
        var percentage = [];
        var key = [];
        var value = [];
        for (var k in result){
            key.push(k);
            value.push(result[k]);
        } 
        for (var i = 0;i < key.length; i++){
            percentage[i] = (value[i]*100).toFixed(2)+"%";
        }
      var pie_data=[];
        pie_data = [{value:  value[0], name:key[0]+percentage[0],value:  value[1], name:key[1]+percentage[1]},
                    {value:  value[2], name:key[2]+percentage[2],value:  value[3], name:key[3]+percentage[3]},
                    {value:  value[4], name:key[4]+percentage[4],value:  value[5], name:key[5]+percentage[5]},
                    {value:  value[6], name:key[6]+percentage[6],value:  value[7], name:key[7]+percentage[7]},
                    {value:  value[8], name:key[8]+percentage[8],value:  value[9], name:key[9]+percentage[9]},
                    {value:  value[10], name:key[10]+percentage[10],value:  value[11], name:key[11]+percentage[11]},
                    {value:  value[12], name:key[12]+percentage[12],value:  value[13], name:key[13]+percentage[13]},
                    {value:  value[14], name:key[14]+percentage[14],value:  value[15], name:key[15]+percentage[15]},
                    {value:  value[16], name:key[16]+percentage[16],value:  value[17], name:key[17]+percentage[17]},
                    {value:  value[18], name:key[18]+percentage[18],value:  value[19], name:key[19]+percentage[19]},
                    {value:  value[20], name:key[20]+percentage[20],value:  value[21], name:key[21]+percentage[21]},
                    {value:  value[22], name:key[22]+percentage[22],value:  value[23], name:key[23]+percentage[23]},
                    {value:  value[24], name:key[24]+percentage[24],value:  value[25], name:key[25]+percentage[25]}];
    
    option = {
        title : {
            text: '',
            x:'center',
            textStyle:{
            fontWeight:'lighter',
            fontSize: 13,
            }        
        },
        // tooltip : {
        //     trigger: 'item',
        //     formatter: "{a} <br/>{b} : {c} ({d}%)"
        // },
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
    var myChart = echarts.init(document.getElementById('pie_div'));
    myChart.setOption(option);
        
    }
    

        function getweibos_data(){   
                var topic = '两会';
                $.ajax({
                    url: "/index/weibos/?&topic=" + topic,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                      
                        chg_weibos(data);
                    }
            });
        }


        function chg_weibos(data){  
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

        function getkeywords_data(){   
                var topic = '两会';
                $.ajax({
                    url: "/index/keywords/?&topic=" + topic,
                    type: "GET",
                    dataType:"json",
                    success: function(data){
                            drawtable(data);
                    }
                });
            }
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
                    if( m > 10) {break;}
                    html += '<tr style="height:25px">';                    
                    html += '<td><b style =\"width:20px\">'+topic+'</b></td>';
                    for (var n = 0 ;n < 5; n++){
                        html += '<td>'+topic_child_keywords[topic][n]+'</td>'
                    }
                    html += "</tr>";
                }
                $("#alternatecolor").append(html);

            }
    
