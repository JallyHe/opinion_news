
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
   })
        var result = [];
        var result1 = [];
        var result2 = [];

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
               
               // for (var i = 0;i < data.length;i++) {
               //      result[i] = data[i][i][0];
               //  };
               //  for (var i = 0;i < data.length;i++) {
               //      result1[i] = data[i][i][1]; 
               //  };
               //  for (var i = 0;i < data.length;i++) {
               //      result2[i] = data[i][i][2][0]+'-'+data[i][i][2][1]; 

               //      var s = i.toString();
               //      if(i==0){
               //          html += '<a value='+ s + ' class="tabLi gColor0 curr" href="javascript:;" style="display: block;">';
               //          html += '<div class="nmTab">'+ result2[i]+ '</div>';
               //          html += '<div class="hvTab">'+result2[i]+'</div></a>';
               // //      }
               //      else{
               //          html += '<a value='+ s + ' class="tabLi gColor0" href="javascript:;" style="display: block;">';
               //          html += '<div class="nmTab">'+ result2[i]+ '</div>';
               //          html += '<div class="hvTab">'+result2[i]+'</div></a>';
               //      }                   
               //  };
               //  $("#Tableselect").append(html);

               drawVisualization(); 
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
   })

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
               // result3[0]=data['10']['10'];
               // result3[1]=data['0']['0'];
               // result3[10]=data['1']['1'];
               // result3[3]=data['2']['2'];
               // result3[2]=data['3']['3'];
               // result3[5]=data['4']['4'];
               // result3[4]=data['5']['5'];
               // result3[7]=data['6']['6'];
              //  result3[6]=data['7']['7'];
               // result3[9]=data['8']['8'];
               // result3[8]=data['9']['9'];

                on_update(result);
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
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
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
    
    // $(document).ready(function(){   //网页加载时执行下面函数
    //     var style = '1';
    //    keyword_data();
    //    switch_curr_add();
    //    getpie_data();
    //    getweibos_data(style);
    //    bindSentimentTabClick();
    // })

    // function bindSentimentTabClick(){
        
    //     $("#Tablebselect").children("a").unbind();

    //     $("#Tableselect").children("a").click(function() {
    //         console.log("avvv");
    //         var select_a = $(this);
    //         var unselect_a = $(this).siblings('a');
    //         if(!select_a.hasClass('curr')) {
    //             select_a.addClass('curr');
    //             unselect_a.removeClass('curr');
    //             style = select_a.attr('value');
    //             getweibos_data(style);
    //         }
    //     });
    // }

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
    
