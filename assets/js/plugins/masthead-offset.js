/*
 * Masthead offset
 *
 * The masthead is position:fixed, so the body needs top padding equal to the
 * masthead's rendered height, and the sidebar needs the same whenever the
 * author profile is not in its collapsed ("Follow" button) state. The height is
 * measured rather than hard-coded because the nav list wraps onto additional
 * lines on narrow viewports.
 *
 * This replaces the upstream greedy-navigation plugin. That plugin collapsed
 * overflowing nav links into a hamburger menu; the hamburger has been removed
 * from this site (the nav wraps instead), so only the offset bookkeeping
 * remains. The nav's class is .masthead__nav, not .greedy-nav, for that reason.
 */

function updateMastheadOffset() {
  var mastheadHeight = $('.masthead').height();

  $('body').css('padding-top', mastheadHeight + 'px');

  if ($('.author__urls-wrapper button').is(':visible')) {
    $('.sidebar').css('padding-top', '');
  } else {
    $('.sidebar').css('padding-top', mastheadHeight + 'px');
  }
}

$(window).on('resize', function () {
  updateMastheadOffset();
});

// Guarded: screen.orientation is absent on older Safari, and an unguarded
// reference here would throw and take the rest of the bundle down with it.
if (screen.orientation) {
  screen.orientation.addEventListener('change', function () {
    updateMastheadOffset();
  });
}

updateMastheadOffset();
