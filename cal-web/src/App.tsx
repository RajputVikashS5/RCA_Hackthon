import './App.css';

function App() {
  return (
    <>
      {/* Top Navigation */}
      <nav className="top-nav container">
        <div className="top-nav-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="var(--ink)" strokeWidth="4" fill="none"/>
          </svg>
          Cal.com
        </div>
        <div className="top-nav-links">
          <a href="#" className="nav-link">Product</a>
          <a href="#" className="nav-link">Solutions</a>
          <a href="#" className="nav-link">Resources</a>
          <a href="#" className="nav-link">Pricing</a>
          <a href="#" className="nav-link">Enterprise</a>
        </div>
        <div className="top-nav-actions">
          <a href="#" className="button-text-link">Sign in</a>
          <button className="button-primary">Sign up free</button>
        </div>
      </nav>

      <main>
        {/* Hero Section */}
        <section className="section hero-band container">
          <div className="hero-grid">
            <div className="hero-content">
              <h1 className="display-xl">The better way to schedule your meetings</h1>
              <p className="title-md">Cal.com is your all-purpose scheduling app for everything from quick coffee chats to complex team meetings.</p>
              <div className="hero-actions">
                <button className="button-primary">Start for free</button>
                <button className="button-secondary">Read the docs</button>
              </div>
            </div>
            <div className="hero-app-mockup-card">
              <div style={{ padding: '24px', backgroundColor: '#fff', borderRadius: '8px', border: '1px solid var(--hairline)'}}>
                <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
                  <div className="avatar-circle">
                    <span className="caption">JS</span>
                  </div>
                  <div>
                    <div className="title-sm">John Smith</div>
                    <div className="caption text-muted">30 Min Meeting</div>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div style={{ border: '1px solid var(--hairline)', borderRadius: '8px', padding: '16px' }}>
                    <div className="caption" style={{ marginBottom: '8px' }}>Select a Day</div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '4px', textAlign: 'center' }}>
                      {['M','T','W','T','F','S','S'].map(d => <div className="caption" key={d}>{d}</div>)}
                      {Array.from({length: 31}).map((_, i) => (
                        <div key={i} className="caption" style={{ padding: '4px', borderRadius: '4px', backgroundColor: i === 14 ? 'var(--ink)' : 'transparent', color: i === 14 ? 'var(--canvas)' : 'inherit' }}>
                          {i + 1}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div className="caption" style={{ marginBottom: '8px' }}>Select a Time</div>
                    {['09:00', '09:30', '10:00', '10:30'].map(t => (
                      <button key={t} className="button-secondary" style={{ width: '100%', height: '36px' }}>{t}</button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Section */}
        <section className="section container">
          <div style={{ textAlign: 'center', marginBottom: '64px' }}>
            <h2 className="display-lg">Your all-purpose scheduling app</h2>
            <p className="title-md" style={{ color: 'var(--muted)', maxWidth: '600px', margin: '16px auto 0' }}>
              With us, appointment scheduling is easy. Connect your calendars, set your availability, and share your link.
            </p>
          </div>
          <div className="feature-grid-3">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="feature-card">
                <div className="button-icon-circular">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L15 8L21 9L16 14L18 20L12 17L6 20L8 14L3 9L9 8L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
                <h3 className="title-md">Time zone intelligent</h3>
                <p className="body-md">Never worry about time zone math again. We automatically detect your invitee's time zone and show your availability in their local time.</p>
              </div>
            ))}
          </div>
        </section>

        {/* Testimonials */}
        <section className="section container">
          <div className="feature-grid-3">
            {[1, 2, 3].map(i => (
              <div key={i} className="testimonial-card">
                <div className="rating-stars">★★★★★</div>
                <p className="body-md">"Cal.com has completely transformed how our team handles external meetings. The API is incredible and the open-source nature gives us complete control."</p>
                <div className="testimonial-header">
                  <div className="avatar-circle">
                    <span className="caption">A{i}</span>
                  </div>
                  <div>
                    <div className="title-sm">Alex Developer</div>
                    <div className="caption text-muted">CTO at Startup {i}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Pricing */}
        <section className="section container">
          <div style={{ textAlign: 'center', marginBottom: '64px' }}>
            <h2 className="display-lg">Pricing that scales with you</h2>
          </div>
          <div className="feature-grid-3">
            <div className="pricing-tier-card">
              <h3 className="title-lg">Personal</h3>
              <div className="display-sm">$0<span className="body-md"> / month</span></div>
              <ul className="body-md" style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '12px', margin: '24px 0' }}>
                <li>✓ Unlimited bookings</li>
                <li>✓ Unlimited event types</li>
                <li>✓ Connect 1 calendar</li>
              </ul>
              <button className="button-secondary" style={{ marginTop: 'auto' }}>Get Started</button>
            </div>
            
            <div className="pricing-tier-card-featured">
              <h3 className="title-lg">Teams</h3>
              <div className="display-sm">$12<span className="body-md"> / user / month</span></div>
              <ul className="body-md" style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '12px', margin: '24px 0' }}>
                <li>✓ Everything in Personal</li>
                <li>✓ Round-robin scheduling</li>
                <li>✓ Remove Cal.com branding</li>
              </ul>
              <button className="button-primary" style={{ backgroundColor: 'var(--canvas)', color: 'var(--ink)', marginTop: 'auto' }}>Start free trial</button>
            </div>

            <div className="pricing-tier-card">
              <h3 className="title-lg">Enterprise</h3>
              <div className="display-sm">Custom</div>
              <ul className="body-md" style={{ listStyle: 'none', padding: 0, display: 'flex', flexDirection: 'column', gap: '12px', margin: '24px 0' }}>
                <li>✓ SAML SSO</li>
                <li>✓ Advanced routing forms</li>
                <li>✓ Dedicated account manager</li>
              </ul>
              <button className="button-secondary" style={{ marginTop: 'auto' }}>Contact Sales</button>
            </div>
          </div>
        </section>

        {/* Pre-footer CTA */}
        <section className="section container">
          <div className="cta-band-light">
            <h2 className="display-sm">Smarter, simpler scheduling</h2>
            <p className="body-md" style={{ color: 'var(--muted)' }}>Join millions of people who use Cal.com to schedule meetings.</p>
            <button className="button-primary">Start for free</button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="container footer-grid">
          <div className="footer-col" style={{ gridColumn: 'span 2' }}>
            <div className="top-nav-logo" style={{ color: 'var(--on-dark)' }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="var(--on-dark)" strokeWidth="4" fill="none"/>
              </svg>
              Cal.com
            </div>
            <p className="body-sm" style={{ maxWidth: '300px', marginTop: '16px' }}>
              The open source Calendly alternative. You are in control of your own data.
            </p>
          </div>
          <div className="footer-col">
            <div className="caption footer-col-title">Product</div>
            <a href="#" className="footer-link body-sm">Features</a>
            <a href="#" className="footer-link body-sm">Integrations</a>
            <a href="#" className="footer-link body-sm">Pricing</a>
            <a href="#" className="footer-link body-sm">Changelog</a>
          </div>
          <div className="footer-col">
            <div className="caption footer-col-title">Developers</div>
            <a href="#" className="footer-link body-sm">Documentation</a>
            <a href="#" className="footer-link body-sm">API Reference</a>
            <a href="#" className="footer-link body-sm">GitHub</a>
          </div>
          <div className="footer-col">
            <div className="caption footer-col-title">Company</div>
            <a href="#" className="footer-link body-sm">About</a>
            <a href="#" className="footer-link body-sm">Blog</a>
            <a href="#" className="footer-link body-sm">Careers</a>
          </div>
        </div>
      </footer>
    </>
  );
}

export default App;
