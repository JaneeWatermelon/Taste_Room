var textarea = $('textarea');

textarea.attr('rows', 4);
textarea.on('keydown', autosize);
$('textarea.fixed').off('keydown');
             
function autosize(){
  var el = this;  
    setTimeout(function(){
      el.style.cssText = 'height:auto; padding:0';
      el.style.cssText = 'height:' + el.scrollHeight + 'px';
    },0);
}