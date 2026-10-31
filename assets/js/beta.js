// Hearth betas: the launch waitlist form, "What's new this week", TestFlight links that keep
// ?via=, and the /beta/thanks and /beta/confirmed pages. Every page works without this file:
// the form posts normally (the API answers with a 303), and What's new stays hidden.
(function () {
  var API = 'https://api.hearthapps.com';
  // The only app names this script will ever put on a page. Anything else in the URL is ignored.
  var NAMES = { suffice: 'Suffice', sated: 'Sated', caloma: 'Caloma', hearken: 'Hearken', trove: 'Trove', ember: 'Ember' };
  var ORDER = ['suffice', 'sated', 'caloma', 'hearken', 'trove', 'ember'];
  var GENERIC = 'Something went wrong on our end. Please try again in a moment, or write to support@hearthapps.com.';

  function decode(s) { try { return decodeURIComponent(s.replace(/\+/g, ' ')); } catch (e) { return ''; } }
  function param(name) {
    var parts = (window.location.search || '').replace(/^\?/, '').split('&');
    for (var i = 0; i < parts.length; i++) {
      var kv = parts[i].split('=');
      if (decode(kv[0]) === name) return decode(kv.slice(1).join('='));
    }
    return null;
  }
  function knownApps(value) {
    var want = String(value || '').toLowerCase().split(',').map(function (s) { return s.trim(); });
    return ORDER.filter(function (k) { return want.indexOf(k) !== -1; });
  }
  function joinNames(keys) {
    var n = keys.map(function (k) { return NAMES[k]; });
    return n.length < 2 ? n.join('') : n.slice(0, -1).join(', ') + ' and ' + n[n.length - 1];
  }

  // A short-link slug from ?via= (Hearth Connect posts). Only plain slugs are passed on.
  var via = param('via') || '';
  if (!/^[A-Za-z0-9_-]{1,64}$/.test(via)) via = '';

  // "Join the beta on TestFlight" goes through /go/tf/<app>, which counts the tap.
  if (via) {
    document.querySelectorAll('a[data-tf]').forEach(function (a) {
      a.href = a.href.split('?')[0] + '?via=' + encodeURIComponent(via);
    });
  }

  // What's new this week, from GET /v1/beta/<app>. Stays hidden when empty or on any failure.
  document.querySelectorAll('[data-whats-new]').forEach(function (sec) {
    var app = sec.getAttribute('data-whats-new');
    if (!NAMES[app] || !window.fetch) return;
    fetch(API + '/v1/beta/' + app, { headers: { Accept: 'application/json' } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        var items = d && Array.isArray(d.whatsNew) ? d.whatsNew.filter(function (s) { return typeof s === 'string' && s.trim(); }) : [];
        if (!items.length) return;
        var ul = sec.querySelector('ul');
        items.slice(0, 6).forEach(function (text) {
          var li = document.createElement('li');
          li.textContent = text.trim();
          ul.appendChild(li);
        });
        var when = d.updatedAt ? new Date(d.updatedAt) : null;
        var dateEl = sec.querySelector('.wn-date');
        if (dateEl && when && !isNaN(when.getTime())) {
          var t = document.createElement('time');
          t.dateTime = when.toISOString();
          t.textContent = when.toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' });
          dateEl.textContent = 'Updated ';
          dateEl.appendChild(t);
          dateEl.hidden = false;
        }
        sec.hidden = false;
      })
      .catch(function () {});
  });

  // The launch waitlist form: POST /v1/waitlist as JSON, then thank you or an error, inline.
  document.querySelectorAll('form[data-waitlist]').forEach(function (form) {
    var fields = form.querySelector('.wl-fields');
    var status = form.querySelector('.wl-status');
    var email = form.querySelector('input[name="email"]');
    var button = form.querySelector('button[type="submit"]');
    var viaInput = form.querySelector('input[name="via"]');
    var pageInput = form.querySelector('input[name="page"]');
    var honey = form.querySelector('input[name="company"]');
    var boxes = form.querySelectorAll('input[type="checkbox"][name="apps"]');
    if (viaInput) viaInput.value = via;

    // On /beta, ?app=sated (or a link from an app's page) can pre-check an app.
    var pre = knownApps(param('app'));
    Array.prototype.forEach.call(boxes, function (b) { if (pre.indexOf(b.value) !== -1) b.checked = true; });

    if (!window.fetch || !window.JSON) return; // the normal form post still works

    function say(text, kind, focusEl) {
      status.className = 'wl-status' + (kind ? ' ' + kind : '');
      status.textContent = text;
      if (focusEl) focusEl.focus();
    }
    function busy(on) {
      button.disabled = on;
      button.textContent = on ? 'Sending…' : 'Notify me';
      form.setAttribute('aria-busy', on ? 'true' : 'false');
    }
    function invalid(el, on) {
      if (!el) return;
      if (on) { el.setAttribute('aria-invalid', 'true'); el.setAttribute('aria-describedby', status.id); }
      else { el.removeAttribute('aria-invalid'); el.removeAttribute('aria-describedby'); }
    }
    if (!status.id) status.id = (email.id || 'wl') + '-status';
    email.addEventListener('input', function () { invalid(email, false); });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var apps = [];
      form.querySelectorAll('input[name="apps"]').forEach(function (i) {
        if (i.type !== 'checkbox' || i.checked) apps.push(i.value);
      });
      if (!apps.length) {
        say('Choose at least one app.', 'err', boxes[0]);
        return;
      }
      var body = { email: email.value.trim(), apps: apps, page: (pageInput && pageInput.value) || window.location.pathname };
      if (via) body.via = via;
      if (honey && honey.value) body.company = honey.value;
      invalid(email, false);
      say('', '');
      busy(true);
      fetch(form.action, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body) })
        .then(function (r) {
          busy(false);
          if (r.ok) {
            fields.hidden = true;
            var names = joinNames(knownApps(apps.join(',')));
            say('Thanks. Check your email to confirm' + (names ? ' you want to hear when ' + names + (apps.length > 1 ? ' launch.' : ' launches.') : '.'), 'ok', status);
          } else if (r.status === 400) {
            invalid(email, true);
            say('That email address doesn’t look right. Check it and try again.', 'err', email);
          } else if (r.status === 429) {
            say('That’s a lot of tries in a row. Please wait a minute, then try again.', 'err', button);
          } else {
            say(GENERIC, 'err', button);
          }
        }, function () {
          busy(false);
          say('We couldn’t reach our server. Check your connection and try again.', 'err', button);
        });
    });
  });

  // /beta/thanks and /beta/confirmed: show the block for ?status=, naming apps from ?apps=.
  var page = document.querySelector('[data-beta-status]');
  if (page) {
    var kind = page.getAttribute('data-beta-status');
    var st = param('status');
    var state = kind === 'thanks' ? (st === 'invalid' ? 'invalid' : 'ok') : (st === 'expired' ? 'expired' : 'ok');
    var apps = knownApps(param('apps'));
    page.querySelectorAll('[data-state]').forEach(function (b) { b.hidden = b.getAttribute('data-state') !== state; });
    var block = page.querySelector('[data-state="' + state + '"]');
    var lede = block && block.querySelector('[data-lede]');
    var names = joinNames(apps), verb = apps.length > 1 ? 'launch' : 'launches';
    if (lede && names && state === 'ok') {
      lede.textContent = kind === 'thanks'
        ? 'We just sent you a link. Tap it to confirm, and we’ll email you once more when ' + names + ' ' + verb + '.'
        : 'We’ll email you once, when ' + names + ' ' + verb + '. Nothing else.';
    }
    if (apps.length === 1 && block) {
      var back = block.querySelector('.cta-row a');
      if (back && state === 'ok') { back.href = '/beta/' + apps[0]; back.textContent = 'Back to the ' + NAMES[apps[0]] + ' beta'; }
    }
    // "Go back and try again" returns to the form with what was typed, when there is a page to go back to.
    var backLink = page.querySelector('[data-back]');
    if (backLink) {
      backLink.addEventListener('click', function (ev) {
        if (window.history.length > 1) { ev.preventDefault(); window.history.back(); }
      });
    }
  }
})();
