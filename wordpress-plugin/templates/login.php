<div class="web-app-login">
    <div class="login-container">
        <div class="login-header">
            <div class="login-logo">
                <!-- PLACE IMAGE: Company logo (200x80px) -->
                <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/logo.png" alt="Company Logo" class="logo">
            </div>
            <h2>Welcome Back</h2>
            <p>Sign in to access your dashboard</p>
        </div>

        <div class="login-content">
            <div class="login-form-container">
                <form id="custom-login-form" class="login-form">
                    <?php wp_nonce_field('custom_login_nonce', 'login_nonce'); ?>
                    
                    <div class="form-group">
                        <label for="user_login">
                            <!-- PLACE IMAGE: User icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/user-icon.png" alt="User">
                            Username or Email
                        </label>
                        <input type="text" id="user_login" name="log" required class="form-input">
                    </div>

                    <div class="form-group">
                        <label for="user_pass">
                            <!-- PLACE IMAGE: Lock icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/lock-icon.png" alt="Password">
                            Password
                        </label>
                        <div class="password-input-group">
                            <input type="password" id="user_pass" name="pwd" required class="form-input">
                            <button type="button" class="password-toggle" onclick="togglePassword()">
                                <!-- PLACE IMAGE: Eye icon (20x20px) -->
                                <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/eye-icon.png" alt="Show Password" id="password-toggle-icon">
                            </button>
                        </div>
                    </div>

                    <div class="form-options">
                        <label class="checkbox-label">
                            <input type="checkbox" name="rememberme" value="forever">
                            <span class="checkmark"></span>
                            Remember me
                        </label>
                        <a href="<?php echo wp_lostpassword_url(); ?>" class="forgot-password">Forgot Password?</a>
                    </div>

                    <button type="submit" class="login-btn">
                        <!-- PLACE IMAGE: Login arrow icon (20x20px) -->
                        <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/login-arrow.png" alt="Login">
                        Sign In
                    </button>

                    <div class="login-divider">
                        <span>or</span>
                    </div>

                    <div class="social-login">
                        <button type="button" class="social-btn google-btn">
                            <!-- PLACE IMAGE: Google icon (24x24px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/google-icon.png" alt="Google">
                            Continue with Google
                        </button>
                        <button type="button" class="social-btn microsoft-btn">
                            <!-- PLACE IMAGE: Microsoft icon (24x24px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/microsoft-icon.png" alt="Microsoft">
                            Continue with Microsoft
                        </button>
                    </div>

                    <div class="signup-link">
                        <p>Don't have an account? <a href="<?php echo wp_registration_url(); ?>">Sign up here</a></p>
                    </div>
                </form>

                <div class="login-features">
                    <h3>Why Choose Our Platform?</h3>
                    <div class="feature-list">
                        <div class="feature-item">
                            <!-- PLACE IMAGE: Security shield icon (32x32px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/security-icon.png" alt="Security">
                            <div class="feature-content">
                                <h4>Advanced Security</h4>
                                <p>Multi-factor authentication and enterprise-grade encryption</p>
                            </div>
                        </div>
                        
                        <div class="feature-item">
                            <!-- PLACE IMAGE: Speed icon (32x32px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/speed-icon.png" alt="Speed">
                            <div class="feature-content">
                                <h4>Lightning Fast</h4>
                                <p>Real-time data processing and instant notifications</p>
                            </div>
                        </div>
                        
                        <div class="feature-item">
                            <!-- PLACE IMAGE: Analytics icon (32x32px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/analytics-icon.png" alt="Analytics">
                            <div class="feature-content">
                                <h4>Smart Analytics</h4>
                                <p>AI-powered insights and predictive intelligence</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="login-sidebar">
                <div class="testimonial">
                    <div class="testimonial-content">
                        <div class="testimonial-avatar">
                            <!-- PLACE IMAGE: Customer photo (60x60px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/testimonial-avatar.jpg" alt="Customer">
                        </div>
                        <blockquote>
                            "This platform transformed our operations completely. 50% reduction in manual work and incredible efficiency gains."
                        </blockquote>
                        <cite>
                            <strong>Sarah Johnson</strong>
                            <span>Operations Manager, TechCorp</span>
                        </cite>
                    </div>
                </div>

                <div class="stats-showcase">
                    <h3>Trusted by Industry Leaders</h3>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-icon">
                                <!-- PLACE IMAGE: Users icon (40x40px) -->
                                <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/users-stat-icon.png" alt="Users">
                            </div>
                            <div class="stat-number">10,000+</div>
                            <div class="stat-label">Active Users</div>
                        </div>
                        
                        <div class="stat-item">
                            <div class="stat-icon">
                                <!-- PLACE IMAGE: Companies icon (40x40px) -->
                                <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/companies-icon.png" alt="Companies">
                            </div>
                            <div class="stat-number">500+</div>
                            <div class="stat-label">Companies</div>
                        </div>
                        
                        <div class="stat-item">
                            <div class="stat-icon">
                                <!-- PLACE IMAGE: Savings icon (40x40px) -->
                                <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/savings-icon.png" alt="Savings">
                            </div>
                            <div class="stat-number">$50M+</div>
                            <div class="stat-label">Cost Savings</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function togglePassword() {
    const passwordInput = document.getElementById('user_pass');
    const toggleIcon = document.getElementById('password-toggle-icon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.src = '<?php echo WAI_PLUGIN_URL; ?>assets/images/eye-off-icon.png';
        toggleIcon.alt = 'Hide Password';
    } else {
        passwordInput.type = 'password';
        toggleIcon.src = '<?php echo WAI_PLUGIN_URL; ?>assets/images/eye-icon.png';
        toggleIcon.alt = 'Show Password';
    }
}
</script>