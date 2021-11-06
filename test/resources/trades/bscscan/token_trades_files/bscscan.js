var czilla_widget = (function() {
    var czilla_widget = {
        push: function(args){
            var nounce = Math.floor(Math.random()*1000000000000);
            var urlCheck = 'https://request-global.czilladx.com/serve/native.php?z=3005fc76e653ed4c445&n='+nounce;
            if(typeof args.mobile === 'undefined') {
                args.mobile = true;
            }
            if(!args.mobile && mobile.true) return;
            var xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.open('GET', urlCheck);
            xhr.onload = function() {
                if (xhr.status === 200) {
                    if(util.isEmptyString(xhr.responseText)) return;
                    var response = JSON.parse(xhr.responseText);
                    if(response.ad === 'undefined') return;
                    response = response.ad;
                    load["initialized"] = function (args,response) {
                        return new this(args,response);
                    };
                    load["initialized"](args,response);
                }else{
                    document.getElementById("c_widget_es").style.visibility = "visible";
                }
            };
            xhr.send();
        }
    };
    var fullAgent = navigator.userAgent,
        userAgent = navigator.userAgent.toLowerCase(),
        mobile = {
            true: /iphone|ipad|android|ucbrowser|iemobile|ipod|blackberry|bada/.test(userAgent)
        },
        util = {
            isEmptyString : function (string) {
                return (
                    (typeof string == 'undefined')
                    ||
                    (string == null)
                    ||
                    (string == false)  //same as: !x
                    ||
                    (string.length == 0)
                    ||
                    (string == "")
                    ||
                    (string.replace(/\s/g,"") == "")
                    ||
                    (!/[^\s]/.test(string))
                    ||
                    (/^\s*$/.test(string))
                );
            }
        },
        load = function (args,content) {
            this.construct(args,content)
        };

    load.prototype = {

        construct: function(args,content){
            this.data = content;
            this.settings = args;
            document.getElementById("c_widget_es").innerHTML = '<div>Sponsored: '+
                '<img src="'+this.data.thumbnail+'" style="width: 20px;height: 20px;" width="20" height="20"> '+
                '<strong>'+this.data.name+'</strong> - '+
                this.data.description_short+
                ' <a href="'+this.data.url+'" rel="nofollow" target="_blank">'+
                ' <strong>'+this.data.cta_button+'</strong>'+
                '</a>'+
                '</div>';
            document.getElementById("c_widget_es").style.visibility = "visible";
            var xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.open('GET', this.data.impressionUrl);
            xhr.onload = function() {
                if (xhr.status !== 200) {
                    console.log("Coinzilla -> Tracking server not responding -> "+xhr.status)
                }
            };
            xhr.send();
        }
    };
    if(typeof window.czilla_widget !== "undefined"){
        for(var i=0; i<window.czilla_widget.length;i++){
            czilla_widget.push(window.czilla_widget[i]);
        }
    }
    return czilla_widget;
})();