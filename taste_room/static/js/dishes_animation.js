let dishes = $(".dishes_wrapper").children();
let dishesLength = $(".dishes_wrapper").children().length;
let indexPrev = 0;
let index = 1;

setInterval(function() {
    $(dishes[indexPrev]).css({
        "transform": "rotate(720deg)",
        "z-index": "1",
    })
    $(dishes[index]).css({
        "transform": "rotate(360deg)",
        "z-index": "2",
    })
    setTimeout(function() {
        $(dishes[indexPrev]).css({
            "opacity": "0",
        })
        $(dishes[index]).css({
            "opacity": "1",
        })
        setTimeout(function() {
            $(dishes[indexPrev]).css({
                "transform": "rotate(0deg)",
            })
            index += 1;
            indexPrev += 1;
            if (index >= dishesLength) {
                index = 0;
            }
            if (indexPrev >= dishesLength) {
                indexPrev = 0;
            }
        }, 500);
    }, 500);
}, 2000)