function document_username() 
{
  var x= readCookie('username');
  if (x) {
    document.write('<a id="please">Your name or callsign: ');
    document.write('<input type="text" value="" name="username" onchange="setusernamecookie()" onclick=""></a>');
    document.usernameform.username.value=x;
  } else {
    document.write('<a id="please"><span id="please1"><b><i>Please log in by typing your name or callsign here (it will be saved for later visits in a cookie):<\/i><\/b></span> ');
    document.write('<input type="text" value="" name="username" onchange="setusernamecookie()" onclick=""></a>');
  }
}

function sendchat()
{
  timeout_idle_restart()
  var xmlHttp;
  try { xmlHttp=new XMLHttpRequest(); }
    catch (e) { try { xmlHttp=new ActiveXObject("Msxml2.XMLHTTP"); }
      catch (e) { try { xmlHttp=new ActiveXObject("Microsoft.XMLHTTP"); }
        catch (e) { alert("Your browser does not support AJAX!"); return false; } } }
  var url="/~~chat";
  var msg=encodeURIComponent(document.chatform.chat.value);
  url=url+"?name="+encodeURIComponent(document.usernameform.username.value)+"&msg="+encodeURIComponent(document.chatform.chat.value);
  xmlHttp.open("GET",url,true);
  xmlHttp.send(null);
  document.chatform.chat.value="";
  return false;
}

function chatnewline(s)
// called by updates fetched from the server
{
  var o=document.getElementById('chatboxnew');
  if (!o) return;
  if (s[0]=='-') {
     // remove line from chatbox
     var div=document.createElement('div');
     div.innerHTML=s;
     s=div.innerHTML;
     var re=new RegExp('<br>'+s.substring(1).replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&")+'.*','g');
     o.innerHTML=o.innerHTML.replace(re,'<br>');
     return;
  }
  // add line to chatbox
  o.innerHTML+='<br>'+s+'\n';
  o.scrollTop=o.scrollHeight;
}

function sendlogclear()
{
  document.logform.comment.value="";
}

function sendlog()
{
  var xmlHttp;
  try { xmlHttp=new XMLHttpRequest(); }
    catch (e) { try { xmlHttp=new ActiveXObject("Msxml2.XMLHTTP"); }
      catch (e) { try { xmlHttp=new ActiveXObject("Microsoft.XMLHTTP"); }
        catch (e) { alert("Your browser does not support AJAX!"); return false; } } }
  var url="/~~loginsert";
  url=url
     +"?name="+encodeURIComponent(document.usernameform.username.value)
     +"&freq="+nominalfreq()
     +"&call="+encodeURIComponent(document.logform.call.value)
     +"&comment="+encodeURIComponent(document.logform.comment.value)
     ;
  xmlHttp.open("GET",url,true);
  xmlHttp.send(null);
  document.logform.call.value="";
  document.logform.comment.value="";
  xmlHttp.onreadystatechange=function()
    {
    if(xmlHttp.readyState==4)
      {
      document.logform.comment.value=xmlHttp.responseText;
      }
    }
  setTimeout("document.logform.comment.value=''",1000);
  return false;
}
