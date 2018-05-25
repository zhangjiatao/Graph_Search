
//获取地址栏中的参数
function getUrlParam(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)"); //构造一个含有目标参数的正则表达式对象
    var r = decodeURI(window.location.search).substr(1).match(reg);  //匹配目标参数
    if (r != null) return unescape(r[2]); return null; //返回参数值
}   

$(document).ready(function(){

    //搜索提交
    $("#button_search").on('click',function(){
        var ques = $('#editbox_search').val();
        var newUrl = 'http://122.112.238.70:8000/?question=' + encodeURI(ques);
        window.location.href = newUrl;
    })

    if(getUrlParam('question')!=null){

        $.ajax({
            type: "GET",
            url: "http://122.112.238.70:8000/getSearch_result/",
            data: "text="+getUrlParam('question'),
            dataType: "json",
            //下面2个参数用于解决跨域问题  
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            success: function(data){
                console.log(data);
                if(data.msg=="0"){
                    //添加问题及答案
                    $("#question").html('问题“'+getUrlParam('question')+'”的答案为：');
                    $("#answer").html(data.anslist);
                    //遍历相关实体列表
                    for (var i = data.nodeList.length - 1; i >= 0; i--) {
                        if(data.nodeList[i].hasOwnProperty('标题'))
                            $("#nodes").append('<h3>'+data.nodeList[i]['标题']+'</h3>');
                        //添加每个相关实体的详细信息
                        for (var key in data.nodeList[i]) {
                            if(key!="标题") $("#nodes").append(key+'：'+data.nodeList[i][key]+'；');
                        }
                    }
                    //传递参数给知识图谱调用
                    var nodes = new Array();
                    var t = 0;
                    for (var i = 0; i < data.nodesGraph.length; i++) {
                        nodes[t++] = data.nodesGraph[i]['name'];
                    }
                    var edges = new Array();
                    var k = 0;
                    for (var i = data.edgesGraph.length - 1; i >= 0; i--) {
                        edges[k++] = String(data.edgesGraph[i]['source']) + 't' + String(data.edgesGraph[i]['target']);
                    }
                    var url = 'http://122.112.238.70:8000/force/?nodes='
                                + encodeURI(nodes) + '&edges=' + encodeURI(edges);
                    $('#knowledgeGraph').attr('src', url);
                }else if(data.msg=="1"){
                    window.alert("服务器返回错误");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                window.alert(textStatus);
            }
        });

    }
    


});


