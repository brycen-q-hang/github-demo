
/*** picture view plugin ****/
(function ($, window, document, undefined) {
    "use strict";

    //an empty function
    var noop = function () {};

    var $body = $('body'),
        $window = $(window),
        $document = $(document);


    //constants
    var ZOOM_CONSTANT = 15; //increase or decrease value for zoom on mouse wheel
    var MOUSE_WHEEL_COUNT = 5; //A mouse delta after which it should stop preventing default behaviour of mouse wheel

    //ease out method
    /*
        t : current time,
        b : intial value,
        c : changed value,
        d : duration
    */

    function easeOutQuart(t, b, c, d) {
        t /= d;
        t--;
        return -c * (t * t * t * t - 1) + b;
    };

    //Load hình ảnh lên web
    //function to check if image is loaded
    function imageLoaded(img) {
        return img.complete && (typeof img.naturalWidth === 'undefined' | img.naturalWidth !== 0);
    }

    var imageViewHtml = '<div class="iv-loader"></div> <div class="iv-snap-view">' + '<div class="iv-snap-image-wrap">' + '<div class="iv-snap-handle"></div>' + '</div>' + '<div class="iv-zoom-slider" id="slider_zoom"><div class="iv-zoom-handle"></div></div></div>' + '<div class="iv-image-view" ><div class="iv-image-wrap" ></div></div>';
    //var imageViewHtml = '<div class="iv-zoom-slider id="slider_zoom"><div class="iv-zoom-handle"></div></div>';

    var slider_zoom = '<div class="iv-zoom-slider">' + '<div class="iv-zoom-handle"></div>' + '</div>';

    function Slider(container, options) {
        this.container = container;
        this.onStart = options.onStart || noop;
        this.onMove = options.onMove || noop;
        this.onEnd = options.onEnd || noop;
        this.sliderId = options.sliderId || 'slider' + Math.ceil(Math.random() * 1000000);
    }

    Slider.prototype.init = function () {
        var self = this,
            container = this.container,
            eventSuffix = '.' + this.sliderId;

        //assign event on snap image wrap
        this.container.on('touchstart' + eventSuffix + ' mousedown' + eventSuffix, function (estart) {
          estart.preventDefault();
            var touchMove = (estart.type == "touchstart" ? "touchmove" : "mousemove") + eventSuffix,
                touchEnd = (estart.type == "touchstart" ? "touchend" : "mouseup") + eventSuffix,
                eOrginal = estart.originalEvent,
                sx = eOrginal.clientX || eOrginal.touches[0].clientX,
                sy = eOrginal.clientY || eOrginal.touches[0].clientY;

            var start = self.onStart(estart, {
                x: sx,
                y: sy
            });

            if (start === false) return;

            var moveListener = function (emove) {

                emove.preventDefault();

                eOrginal = emove.originalEvent;

                //Kéo ảnh
                //get the cordinates
                var mx = eOrginal.clientX,
                    my = eOrginal.clientY;

                self.onMove(emove, {
                    dx: mx - sx,
                    dy: my - sy,
                    mx: mx,
                    my: my
                });

            };

            var endListener = function () {
                $document.off(touchMove, moveListener);
                $document.off(touchEnd, endListener);
                self.onEnd();
            };

            $document.on(touchMove, moveListener);
            $document.on(touchEnd, endListener);
        });

        return this;
    }


    function ImageViewer(container, options) {
        var self = this;

        if (container.is('#iv-container')) {
            self._fullPage = true;
        }

        self.container = container;
        options = self.options = $.extend({}, ImageViewer.defaults, options);

        self.zoomValue = 100;

        if (!container.find('.snap-view').length) {
            //container.append(slider_zoom)
            container.prepend(imageViewHtml);
            
        }

        container.addClass('iv-container');

        if (container.css('position') == 'static') container.css('position', 'relative');

        self.snapView = container.find('.iv-snap-view');
        self.snapImageWrap = container.find('.iv-snap-image-wrap');
        self.imageWrap = container.find('.iv-image-wrap');
        self.snapHandle = container.find('.iv-snap-handle');
        self.zoomHandle = container.find('.iv-zoom-handle');
        self._viewerId = 'iv' + Math.floor(Math.random() * 1000000);
    }


    ImageViewer.prototype = {
        constructor: ImageViewer,
        _init: function () {
            var viewer = this,
                options = viewer.options,
                zooming = false, // tell weather we are zooming trough touch
                container = this.container;

            var eventSuffix = '.' + viewer._viewerId;

            //cache dom refrence
            var snapHandle = this.snapHandle;
            var snapImgWrap = this.snapImageWrap;
            var imageWrap = this.imageWrap;

            var snapSlider = new Slider(snapImgWrap, {
                sliderId: viewer._viewerId,
                //Kéo thả chuột trên hình
                onStart: function () {

                    if (!viewer.loaded) return false;

                    var handleStyle = snapHandle[0].style;

                    this.curHandleTop = parseFloat(handleStyle.top);
                    this.curHandleLeft = parseFloat(handleStyle.left);
                    this.handleWidth = parseFloat(handleStyle.width);
                    this.handleHeight = parseFloat(handleStyle.height);
                    this.width = snapImgWrap.width();
                    this.height = snapImgWrap.height();

                    //stop momentum on image
                    clearInterval(imageSlider.slideMomentumCheck);
                    cancelAnimationFrame(imageSlider.sliderMomentumFrame);
                },
                onMove: function (e, position) {
                    var xPerc = this.curHandleLeft + position.dx * 100 / this.width,
                        yPerc = this.curHandleTop + position.dy * 100 / this.height;

                    xPerc = Math.max(0, xPerc);
                    xPerc = Math.min(100 - this.handleWidth, xPerc);

                    yPerc = Math.max(0, yPerc);
                    yPerc = Math.min(100 - this.handleHeight, yPerc);


                    var containerDim = viewer.containerDim,
                        imgWidth = viewer.imageDim.w * (viewer.zoomValue / 100),
                        imgHeight = viewer.imageDim.h * (viewer.zoomValue / 100),
                        imgLeft = imgWidth < containerDim.w ? (containerDim.w - imgWidth) / 2 : -imgWidth * xPerc / 100,
                        imgTop = imgHeight < containerDim.h ? (containerDim.h - imgHeight) / 2 : -imgHeight * yPerc / 100;

                    snapHandle.css({
                        top: yPerc + '%',
                        left: xPerc + '%'
                    })

                    viewer.currentImg.css({
                        left: imgLeft,
                        top: imgTop
                    })

                    viewer.compareImg.css({
                        left: imgLeft,
                        top: imgTop
                    })
                }
            }).init();


            /*Add slide interaction to image*/
            var imageSlider = viewer._imageSlider = new Slider(imageWrap, {
                sliderId: viewer._viewerId,
                onStart: function (e, position) {
                    if (!viewer.loaded) return false;
                    if (zooming) return;
                    var self = this;
                    snapSlider.onStart();
                    self.imgWidth = viewer.imageDim.w * viewer.zoomValue / 100;
                    self.imgHeight = viewer.imageDim.h * viewer.zoomValue / 100;

                    self.positions = [position, position];

                    self.startPosition = position;
                },
                onMove: function (e, position) {
                    if (zooming) return;
                    this.currentPos = position;

                    snapSlider.onMove(e, {
                        dx: -position.dx * snapSlider.width / this.imgWidth,
                        dy: -position.dy * snapSlider.height / this.imgHeight
                    });
                },
                
            }).init();

            //Kéo thả chuột để trượt hình ảnh
            /*Add zoom interation in mouse wheel*/
            var changedDelta = 0;
            imageWrap.on("mousewheel" + eventSuffix + " DOMMouseScroll" + eventSuffix, function (e) {

                if(!options.zoomOnMouseWheel) return;

                if (!viewer.loaded) return;


                //clear all animation frame and interval
                viewer._clearFrames();

                // cross-browser wheel delta
                var delta = Math.max(-1, Math.min(1, (e.originalEvent.wheelDelta || -e.originalEvent.detail))),
                    zoomValue = viewer.zoomValue * (100 + delta * ZOOM_CONSTANT) / 100;

                if(!(zoomValue >= 100 && zoomValue <= options.maxZoom)){
                    changedDelta += Math.abs(delta);
                }
                else{
                    changedDelta = 0;
                }

                if(changedDelta > MOUSE_WHEEL_COUNT) return;

                e.preventDefault();

                var contOffset = container.offset(),
                    x = (e.pageX || e.originalEvent.pageX) - contOffset.left,
                    y = (e.pageY || e.originalEvent.pageY) - contOffset.top;



                viewer.zoom(zoomValue, {
                    x: x,
                    y: y
                });

                //show the snap viewer
                //showSnapView();
            });

           
            // dbclick để zoom
            //handle double tap for zoom in and zoom out
            //var touchtime = 0,
                //point;
            imageWrap.on('dblclick' + eventSuffix, function (e) {

                        //console.log('src: ' + viewer.zoomValue)
                        
                        if (viewer.zoomValue <= 200) {
                            viewer.zoom(300)

                            //console.log(Date.now() - touchtime)
                            //console.log(viewer.zoomValue + ' & ' + options.zoomValue)
                            console.log('in')

                        } else {
                            //console.log(viewer.zoomValue + ' & ' + options.zoomValue)
                            viewer.zoom(100)
                            //viewer.resetZoom()
                            console.log('out')              
                        }
                    
            });

            //Kéo slider zoom phía dưới image small
            //zoom in zoom out using zoom handle
            var slider = viewer.snapView.find('.iv-zoom-slider');
            var zoomSlider = new Slider(slider, {
                sliderId: viewer._viewerId,
                onStart: function (eStart) {

                    if (!viewer.loaded) return false;

                    this.leftOffset = slider.offset().left;
                    this.handleWidth = viewer.zoomHandle.width();
                    this.onMove(eStart);

                },
                onMove: function (e, position) {
                    var newLeft = (e.pageX || e.originalEvent.touches[0].pageX) - this.leftOffset - this.handleWidth / 2;

                    newLeft = Math.max(0, newLeft);
                    newLeft = Math.min(viewer._zoomSliderLength, newLeft);

                    var zoomValue = 100 + (options.maxZoom - 100) * newLeft / viewer._zoomSliderLength;
                    console.log($('.iv-zoom-handle').css('left'))
                    viewer.zoom(zoomValue);
                }
            }).init();


            //Quan trọng , nếu ko có thì sẽ trở thành 1 hình ảnh tỉnh và ko tương tác đc
            //calculate elments size on window resize
            if (options.refreshOnResize) $window.on('resize' + eventSuffix, function () {
                //console.log("viewer refresh")
                //viewer.refresh()
            });

           
        },

        //Tính toán để zoom, nếu ko sẽ ko zoom đc và hình luôn trong trangj thái Loading
        //method to zoom images
        zoom: function (perc, point) {
            perc = Math.max(100, perc);

            point = point || {
                x: this.containerDim.w / 2,
                y: this.containerDim.h / 2
            };

            var self = this,
                maxZoom = this.options.maxZoom,
                curPerc = this.zoomValue,
                curImg = this.currentImg,
                compareImg = this.compareImg,
                containerDim = this.containerDim,
                curLeft = parseFloat(curImg.css('left')),
                curTop = parseFloat(curImg.css('top'));


            self._clearFrames();

            var step = 0;

            //calculate base top,left,bottom,right
            var containerDim = self.containerDim,
                imageDim = self.imageDim;
            var baseLeft = (containerDim.w - imageDim.w) / 2,
                baseTop = (containerDim.h - imageDim.h) / 2,
                baseRight = containerDim.w - baseLeft,
                baseBottom = containerDim.h - baseTop;

            function zoom() {
                step++;

                if (step < 20) {
                    self._zoomFrame = requestAnimationFrame(zoom);
                }

                var tickZoom = Math.min(maxZoom, easeOutQuart(step, curPerc, perc - curPerc, 20));

                var ratio = tickZoom / curPerc,
                    imgWidth = self.imageDim.w * tickZoom / 100,
                    imgHeight = self.imageDim.h * tickZoom / 100,
                    newLeft = -((point.x - curLeft) * ratio - point.x),
                    newTop = -((point.y - curTop) * ratio - point.y);
                
                //Ổn định kích thước ảnh lớn khi zoom, nếu ko có vẫn chạy tốt & xuất hiện 1 bug nhỏ khi zoom out hết mức
                //fix for left and top
                newLeft = Math.min(newLeft, baseLeft);
                newTop = Math.min(newTop, baseTop);

                //fix for right and bottom
                if((newLeft + imgWidth) < baseRight){
                    newLeft = (self.containerDim.w - imgWidth) ; //newLeft - (newLeft + imgWidth - baseRig
                }

                if((newTop + imgHeight) < baseBottom){
                    newTop = (self.containerDim.h - imgHeight) ; //newLeft - (newLeft + imgWidth - baseRig
                }

                curImg.css({
                    height: imgHeight + 'px',
                    width: imgWidth + 'px',
                    left: newLeft + 'px',
                    top: newTop + 'px'
                });

                compareImg.css({
                    height: 'auto',
                    width: imgWidth + 'px',
                    left: newLeft + 'px',
                    top: newTop + 'px'
                });

                self.zoomValue = tickZoom;

                self._resizeHandle(imgWidth, imgHeight, newLeft, newTop);

                //slider zoom ko kéo đc nhưng để chuột vào kéo vẫn dc & hình ảnh vẫn hiển thị đúng
                //update zoom handle position
                self.zoomHandle.css('left', ((tickZoom - 100) * self._zoomSliderLength) / (maxZoom - 100) + 'px');
            }

            zoom();
        },
        //ko có chạy ko đc
        _clearFrames: function () {
            //clearInterval(this._imageSlider.slideMomentumCheck);
            //cancelAnimationFrame(this._imageSlider.sliderMomentumFrame);
            cancelAnimationFrame(this._zoomFrame)
        },
        //ko có vẫn chạy đc
        resetZoom: function () {
            this.zoom(this.options.zoomValue);
        },

        //calculate dimensions of image, container and reset the image
        _calculateDimensions: function () {
            //calculate content width of image and snap image
            var self = this,
                curImg = self.currentImg,
                compareImg = self.compareImg,
                container = self.container,
                snapView = self.snapView,
                imageWidth = curImg.width(),
                imageHeight = curImg.height(),
                contWidth = container.width(),
                contHeight = container.height(),
                snapViewWidth = snapView.innerWidth(),
                snapViewHeight = snapView.innerHeight();

            //set the container dimension
            self.containerDim = {
                w: contWidth,
                h: contHeight
            }

            //set the image dimension
            var imgWidth, imgHeight, ratio = imageWidth / imageHeight;

            imgWidth = (imageWidth > imageHeight && contHeight >= contWidth) || ratio * contHeight > contWidth ? contWidth : ratio * contHeight;

            imgHeight = imgWidth / ratio;

            self.imageDim = {
                w: imgWidth,
                h: imgHeight
            }
           
            // issue important zoom ko dc
            //this.options.maxZoom = Math.max(maxPercWidth, maxPercHeight)

            //reset image position and zoom
            compareImg.css({
                width: imgWidth + 'px',
                height: 'auto',
                left: (contWidth - imgWidth) / 2 + 'px',
                top: (contHeight - imgHeight) / 2 + 'px',
                'max-width': 'none',
                'max-height': 'none'
            });
            curImg.css({
                width: imgWidth + 'px',
                height: imgHeight + 'px',
                left: (contWidth - imgWidth) / 2 + 'px',
                top: (contHeight - imgHeight) / 2 + 'px',
                'max-width': 'none',
                'max-height': 'none'
            });

            //set the snap Image dimension
            var snapWidth = imgWidth > imgHeight ? snapViewWidth : imgWidth * snapViewHeight / imgHeight,
                snapHeight = imgHeight > imgWidth ? snapViewHeight : imgHeight * snapViewWidth / imgWidth;

            //ko có cũng ko sao
            self.snapImageDim = {
                w: snapWidth,
                h: snapHeight
            }
                /*Vẫn chạy ok & bug là image small ko hiển thị & zoom all ok*/
            self.snapImg.css({
                width: snapWidth,
                height: snapHeight
            });

            //calculate zoom slider area
            self._zoomSliderLength = snapViewWidth - self.zoomHandle.outerWidth();

        },

        refresh: function () {
            if (!this.loaded) return;
            this._calculateDimensions();
            this.resetZoom();
        },
        _resizeHandle: function (imgWidth, imgHeight, imgLeft, imgTop) {
            var curImg = this.currentImg,
                imageWidth = imgWidth || this.imageDim.w * this.zoomValue / 100,
                imageHeight = imgHeight || this.imageDim.h * this.zoomValue / 100,
                left = Math.max(-(imgLeft || parseFloat(curImg.css('left'))) * 100 / imageWidth, 0),
                top = Math.max(-(imgTop || parseFloat(curImg.css('top'))) * 100 / imageHeight, 0),
                handleWidth = Math.min(this.containerDim.w * 100 / imageWidth, 100),
                handleHeight = Math.min(this.containerDim.h * 100 / imageHeight, 100);

            this.snapHandle.css({
                top: top + '%',
                left: left + '%',
                width: handleWidth + '%',
                height: handleHeight + '%'
            });
        },
        
        load: function (image, hiResImg, compare, hiResCompare) {
            var self = this,
                container = this.container;

            container.find('.iv-snap-image,.iv-large-image').remove();
            var snapImageWrap = this.container.find('.iv-snap-image-wrap');
            snapImageWrap.prepend('<img class="iv-snap-image" style="width:120px; height: 90px;" src="' + image + '" />');
            this.imageWrap.prepend('<img class="iv-large-image" src="' + image + '" />');
            /* */
            $(document).find(".iv-large-image-ss").attr('src', image);

            if (hiResImg) {
                this.imageWrap.append('<img class="iv-large-image" src="' + hiResImg + '" />')
            }

            if(compare) {
                this.imageWrap.append('<img class="iv-large-compare" src="' + compare + '" />');
            }

            var currentImg = this.currentImg = this.container.find('.iv-large-image');
            var compareImg = this.compareImg = this.container.find('.iv-large-compare');
            this.snapImg = this.container.find('.iv-snap-image');
            self.loaded = false;

            //show loader
            container.find('.iv-loader').show();
            currentImg.hide();
            compareImg.css('opacity', 0);
            self.snapImg.hide();

            //refresh the view
            function refreshView() {
                self.loaded = true;
                self.zoomValue = 100;

                //reset zoom of images
                currentImg.show();
                self.snapImg.show();
                self.refresh();
                self.resetZoom();

                //hide loader
                container.find('.iv-loader').hide();
            }

            if (imageLoaded(currentImg[0])) {
                refreshView();
            } else {
                $(currentImg[0]).on('load', refreshView);
            }

        },
        setCompareAlpha: function(alpha) {
            /*Add shift binding for image compare toggle*/
            this.compareImg.css('opacity', alpha)
        }
    }

    ImageViewer.defaults = {
        zoomValue: 100,
        snapView: true,
        maxZoom: 300,
        refreshOnResize: true,
        zoomOnMouseWheel : true
    }

    window.ImageViewer = function (container, options) {
        var imgElm, imgSrc, compareElm, compareSrc, hiResImg, hiResCompare;
        if (!(container && (typeof container == "string" || container instanceof Element || container[0] instanceof Element))) {
            options = container;
            container = $('#iv-container');
        }

        container = $(container);

        if (container.is('img')) {
            imgElm = container;
            imgSrc = imgElm[0].src;
            hiResImg = imgElm.attr('high-res-src') || imgElm.attr('data-high-res-src');
            container = imgElm.wrap('<div class="iv-container" style="display:inline-block; overflow:hidden"></div>').parent();
            imgElm.css({
                opacity: 0,
                position: 'relative',
                zIndex: -1
            });
        } else {
            imgSrc = container.attr('src') || container.attr('data-src');
            compareSrc = container.attr('compare-src') || container.attr('data-compare-src');
            hiResImg = container.attr('high-res-src') || container.attr('data-high-res-src');
        }


        var viewer = new ImageViewer(container, options);
        viewer._init();

        if (imgSrc) viewer.load(imgSrc, hiResImg, compareSrc, hiResCompare);

        return viewer;
    };


}((window.jQuery), window, document));



