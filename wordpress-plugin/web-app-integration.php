<?php
/**
 * Plugin Name: Web App Integration
 * Description: Custom plugin for user authentication, dashboard, and search functionality
 * Version: 1.0.0
 * Author: Your Company
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('WAI_PLUGIN_URL', plugin_dir_url(__FILE__));
define('WAI_PLUGIN_PATH', plugin_dir_path(__FILE__));

class WebAppIntegration {
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        register_activation_hook(__FILE__, array($this, 'activate'));
    }
    
    public function init() {
        // Add shortcodes
        add_shortcode('user_dashboard', array($this, 'user_dashboard_shortcode'));
        add_shortcode('advanced_search', array($this, 'search_shortcode'));
        add_shortcode('user_login', array($this, 'login_shortcode'));
        
        // Handle AJAX requests
        add_action('wp_ajax_user_search', array($this, 'handle_search'));
        add_action('wp_ajax_nopriv_user_search', array($this, 'handle_search'));
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script('web-app-js', WAI_PLUGIN_URL . 'assets/app.js', array('jquery'), '1.0.0', true);
        wp_enqueue_style('web-app-css', WAI_PLUGIN_URL . 'assets/style.css', array(), '1.0.0');
        
        wp_localize_script('web-app-js', 'ajax_object', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('web_app_nonce')
        ));
    }
    
    public function activate() {
        $this->create_tables();
        flush_rewrite_rules();
    }
    
    private function create_tables() {
        global $wpdb;
        
        $table_name = $wpdb->prefix . 'user_data';
        
        $charset_collate = $wpdb->get_charset_collate();
        
        $sql = "CREATE TABLE $table_name (
            id mediumint(9) NOT NULL AUTO_INCREMENT,
            user_id bigint(20) NOT NULL,
            data_type varchar(50) NOT NULL,
            data_value text NOT NULL,
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) $charset_collate;";
        
        require_once(ABSPATH . 'wp-admin/includes/upgrade.php');
        dbDelta($sql);
    }
    
    public function user_dashboard_shortcode() {
        if (!is_user_logged_in()) {
            return '<p>Please log in to access your dashboard.</p>';
        }
        
        ob_start();
        include WAI_PLUGIN_PATH . 'templates/dashboard.php';
        return ob_get_clean();
    }
    
    public function search_shortcode() {
        ob_start();
        include WAI_PLUGIN_PATH . 'templates/search.php';
        return ob_get_clean();
    }
    
    public function login_shortcode() {
        if (is_user_logged_in()) {
            return '<p>You are already logged in. <a href="' . wp_logout_url() . '">Logout</a></p>';
        }
        
        ob_start();
        include WAI_PLUGIN_PATH . 'templates/login.php';
        return ob_get_clean();
    }
    
    public function handle_search() {
        check_ajax_referer('web_app_nonce', 'nonce');
        
        $search_term = sanitize_text_field($_POST['search_term']);
        $filters = isset($_POST['filters']) ? $_POST['filters'] : array();
        
        $results = $this->perform_search($search_term, $filters);
        
        wp_send_json_success($results);
    }
    
    private function perform_search($term, $filters) {
        $args = array(
            'post_type' => 'any',
            's' => $term,
            'posts_per_page' => 20
        );
        
        if (!empty($filters)) {
            $args['meta_query'] = array();
            foreach ($filters as $key => $value) {
                $args['meta_query'][] = array(
                    'key' => $key,
                    'value' => $value,
                    'compare' => 'LIKE'
                );
            }
        }
        
        $query = new WP_Query($args);
        return $query->posts;
    }
}

new WebAppIntegration();
?>