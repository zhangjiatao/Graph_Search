$(document).ready(function(){

    $.ajax({
            type: "GET",
            url: "http://122.112.238.70:8000/getSearch_result/",
            data: "text=南京有多少个区",
            dataType: "json",
            //下面2个参数用于解决跨域问题  
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            success: function(data){
                console.log(data);
                if(data.msg=="0"){
                    $("#question").html('问题“南京有多少个区”的答案为：');
                    $("#answer").html(data.anslist);
                    for (var i = data.nodeList.length - 1; i >= 0; i--) {
                        if(data.nodeList[i].hasOwnProperty('标题'))
                            $("#nodes").append('<h4>'+data.nodeList[i]['标题']+'</h4>');
                        for (var key in data.nodeList[i]) {
                            console.log(key);     //获取key值
                            console.log(data.nodeList[i][key]); //获取对应的value值
                            if(key!="标题") $("#nodes").append('<small>'+key+'：'+data.nodeList[i][key]+'；</small>');
                        }
                    }
                }else if(data.msg=="1"){
                    window.alert("服务器返回错误");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest);
                window.alert(textStatus);
                window.alert(errorThrown);
            }
        });


    
    //搜索提交
    $("#button_search").on('click',function(){
        var ques = $('#editbox_search').val();

        $.ajax({
            type: "GET",
            url: "http://122.112.238.70:8000/getSearch_result/",
            data: "text="+ques,
            dataType: "json",
            //下面2个参数用于解决跨域问题  
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            success: function(data){
                if(data.msg=="0"){
                    $("#question").html('问题“'+ques+'”的答案为：');
                    $("#answer").html(data.anslist);
                }else if(data.msg=="1"){
                    window.alert("服务器返回错误");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log(XMLHttpRequest);
                window.alert(textStatus);
                window.alert(errorThrown);
            }
        });
    })

   
});

// // d3图生成
               
//         var nodes = [ { name: "桂林"    }, { name: "广州" },
//                       { name: "厦门"    }, { name: "杭州"   },
//                       { name: "上海"   }, { name: "青岛"    },
//                       { name: "天津"    } ];
                     
//         var edges = [  { source : 0  , target: 1 } , { source : 0  , target: 2 } ,
//                        { source : 0  , target: 3 } , { source : 1  , target: 4 } ,
//                        { source : 1  , target: 5 } , { source : 1  , target: 6 }  ];    
        
//         var width = 340;
//         var height = 340;
        
        
//         var svg = d3.select("#knowledgeGraph")
//                     .append("svg")
//                     .attr("width",width)
//                     .attr("height",height);
        
//         var force = d3.layout.force()
//                 .nodes(nodes)       //指定节点数组
//                 .links(edges)       //指定连线数组
//                 .size([width,height])   //指定范围
//                 .linkDistance(150)  //指定连线长度
//                 .charge(-400);  //相互之间的作用力

//         force.start();  //开始作用

//         console.log(nodes);
//         console.log(edges);
        
//         //添加连线      
//         var svg_edges = svg.selectAll("line")
//                             .data(edges)
//                             .enter()
//                             .append("line")
//                             .style("stroke","#ccc")
//                             .style("stroke-width",1);
        
//         var color = d3.scale.category20();
                
//         //添加节点          
//         var svg_nodes = svg.selectAll("circle")
//                             .data(nodes)
//                             .enter()
//                             .append("circle")
//                             .attr("r",20)
//                             .style("fill",function(d,i){
//                                 return color(i);
//                             })
//                             .call(force.drag);  //使得节点能够拖动

//         //添加描述节点的文字
//         var svg_texts = svg.selectAll("text")
//                             .data(nodes)
//                             .enter()
//                             .append("text")
//                             .style("fill", "black")
//                             .attr("dx", 20)
//                             .attr("dy", 8)
//                             .text(function(d){
//                                 return d.name;
//                             });
                    

//         force.on("tick", function(){    //对于每一个时间间隔
        
//              //更新连线坐标
//              svg_edges.attr("x1",function(d){ return d.source.x; })
//                     .attr("y1",function(d){ return d.source.y; })
//                     .attr("x2",function(d){ return d.target.x; })
//                     .attr("y2",function(d){ return d.target.y; });
             
//              //更新节点坐标
//              svg_nodes.attr("cx",function(d){ return d.x; })
//                     .attr("cy",function(d){ return d.y; });

//              //更新文字坐标
//              svg_texts.attr("x", function(d){ return d.x; })
//                 .attr("y", function(d){ return d.y; });
//         });


