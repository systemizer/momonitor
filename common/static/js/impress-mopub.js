var impress = impress();
impress.init();

setTimeout("location.reload()",1000*60*10) //reload page after 10 minutes because i dont want to use websockets

document.addEventListener('impress:stepenter', function(e){
    if (typeof timing !== 'undefined') clearInterval(timing);

    var duration = (e.target.getAttribute('data-transition-duration') ? e.target.getAttribute('data-transition-duration') : 10000);
    timing = setInterval(impress.next, duration);
})
