$(function () {
  $('[data-toggle="tooltip"]').tooltip();
  $(".share-link").on("click", function (e) {
    e.preventDefault();
    var $this = $(this);
    var title = encodeURIComponent($this.data("title") || document.title);
    var url = encodeURIComponent($this.data("url") || win.location);
    if ($this.hasClass("twitter")) {
      open("http://twitter.com/share?url=" + url + "&text=" + title, "twitter-share", "height=400,width=550,resizable=1,toolbar=0,menubar=0,status=0,location=0");
    } else if ($this.hasClass("facebook")) {
      open("http://facebook.com/sharer.php?s=100&p[url]=" + url, "facebook-share", "height=380,width=660,resizable=0,toolbar=0,menubar=0,status=0,location=0,scrollbars=0");
    } else if ($this.hasClass("gplus")) {
      open("https://plus.google.com/share?url=" + url, "gshare", "height=270,width=630,resizable=0,toolbar=0,menubar=0,status=0,location=0,scrollbars=0");
    } else if ($this.hasClass("linkedin")) {
      open("http://www.linkedin.com/shareArticle?mini=true&url=" + url + "&text=" + title, "linkedin-share", "height=270,width=630,resizable=0,toolbar=0,menubar=0,status=0,location=0,scrollbars=0");
    }
  });
  $('.jobCreate input[name="will_sponsor"][value="False"]').on("click", function (e) {
    $('.jobCreate .offer').addClass('hidden');
  });
  $('.jobCreate input[name="will_sponsor"][value="True"]').on("click", function (e) {
    $('.jobCreate .offer').removeClass('hidden');
  });
  $('#mobile-btn-more').on("click", function() {
    $('#mobileNav').toggleClass('menu-opened');
    $('body').toggleClass('noscroll');
  });
});
