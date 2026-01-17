jQuery(document).ready(function($) {
    
    // Advanced Search Functionality
    $('#advanced-search-form').on('submit', function(e) {
        e.preventDefault();
        performSearch();
    });
    
    // Clear filters
    $('#clear-filters').on('click', function() {
        $('#advanced-search-form')[0].reset();
        $('#search-results-container').html('<div class="no-results"><div class="no-results-icon"><img src="' + ajax_object.plugin_url + 'assets/images/no-results.png" alt="No Results"></div><h3>Start your search</h3><p>Enter keywords above to find what you\'re looking for</p></div>');
        $('#results-count').text('0 results found');
    });
    
    // View toggle
    $('.view-btn').on('click', function() {
        $('.view-btn').removeClass('active');
        $(this).addClass('active');
        
        var view = $(this).data('view');
        $('#search-results-container').removeClass('grid-view list-view').addClass(view + '-view');
    });
    
    // Sort change
    $('#sort-by').on('change', function() {
        if ($('#search-results-container .result-item').length > 0) {
            performSearch();
        }
    });
    
    // Custom login form
    $('#custom-login-form').on('submit', function(e) {
        e.preventDefault();
        
        var formData = {
            action: 'custom_user_login',
            log: $('#user_login').val(),
            pwd: $('#user_pass').val(),
            rememberme: $('input[name="rememberme"]').is(':checked'),
            nonce: $('input[name="login_nonce"]').val()
        };
        
        $.ajax({
            url: ajax_object.ajax_url,
            type: 'POST',
            data: formData,
            beforeSend: function() {
                $('.login-btn').prop('disabled', true).text('Signing in...');
            },
            success: function(response) {
                if (response.success) {
                    window.location.href = response.data.redirect_url || '/dashboard';
                } else {
                    showLoginError(response.data.message);
                }
            },
            error: function() {
                showLoginError('Login failed. Please try again.');
            },
            complete: function() {
                $('.login-btn').prop('disabled', false).html('<img src="' + ajax_object.plugin_url + 'assets/images/login-arrow.png" alt="Login"> Sign In');
            }
        });
    });
    
    // Dashboard quick actions
    $('.action-btn').on('click', function() {
        var action = $(this).text().trim();
        
        switch(action) {
            case 'New Project':
                openNewProjectModal();
                break;
            case 'Upload File':
                openFileUploadModal();
                break;
            case 'Generate Report':
                openReportModal();
                break;
        }
    });
    
    // Real-time notifications (simulate)
    if ($('.web-app-dashboard').length > 0) {
        setInterval(checkNotifications, 30000); // Check every 30 seconds
    }
    
    // Search suggestions
    $('.suggestion-tag').on('click', function() {
        var suggestion = $(this).text();
        $('#search-term').val(suggestion);
        performSearch();
    });
    
    function performSearch() {
        var searchTerm = $('#search-term').val();
        var filters = {};
        
        // Collect filter values
        $('#advanced-search-form select').each(function() {
            var name = $(this).attr('name');
            var value = $(this).val();
            if (value && name) {
                var filterName = name.replace('filters[', '').replace(']', '');
                filters[filterName] = value;
            }
        });
        
        var sortBy = $('#sort-by').val();
        
        $.ajax({
            url: ajax_object.ajax_url,
            type: 'POST',
            data: {
                action: 'user_search',
                search_term: searchTerm,
                filters: filters,
                sort_by: sortBy,
                nonce: ajax_object.nonce
            },
            beforeSend: function() {
                $('#search-results-container').html('<div class="loading">Searching...</div>');
            },
            success: function(response) {
                if (response.success) {
                    displaySearchResults(response.data);
                } else {
                    $('#search-results-container').html('<div class="error">Search failed. Please try again.</div>');
                }
            },
            error: function() {
                $('#search-results-container').html('<div class="error">Search failed. Please try again.</div>');
            }
        });
    }
    
    function displaySearchResults(results) {
        var container = $('#search-results-container');
        var html = '';
        
        if (results.length === 0) {
            html = '<div class="no-results"><div class="no-results-icon"><img src="' + ajax_object.plugin_url + 'assets/images/no-results.png" alt="No Results"></div><h3>No results found</h3><p>Try adjusting your search terms or filters</p></div>';
        } else {
            results.forEach(function(result) {
                html += '<div class="result-item">';
                html += '<div class="result-icon"><img src="' + getResultIcon(result.post_type) + '" alt="' + result.post_type + '"></div>';
                html += '<div class="result-content">';
                html += '<h3><a href="' + result.permalink + '">' + result.post_title + '</a></h3>';
                html += '<p>' + (result.post_excerpt || result.post_content.substring(0, 150) + '...') + '</p>';
                html += '<div class="result-meta">';
                html += '<span class="result-type">' + result.post_type + '</span>';
                html += '<span class="result-date">' + formatDate(result.post_date) + '</span>';
                html += '</div>';
                html += '</div>';
                html += '</div>';
            });
        }
        
        container.html(html);
        $('#results-count').text(results.length + ' results found');
    }
    
    function getResultIcon(postType) {
        var icons = {
            'post': ajax_object.plugin_url + 'assets/images/post-icon.png',
            'page': ajax_object.plugin_url + 'assets/images/page-icon.png',
            'document': ajax_object.plugin_url + 'assets/images/document-icon.png',
            'project': ajax_object.plugin_url + 'assets/images/project-icon.png'
        };
        
        return icons[postType] || ajax_object.plugin_url + 'assets/images/default-icon.png';
    }
    
    function formatDate(dateString) {
        var date = new Date(dateString);
        return date.toLocaleDateString();
    }
    
    function showLoginError(message) {
        var errorHtml = '<div class="login-error" style="background: #f8d7da; color: #721c24; padding: 10px; border-radius: 4px; margin: 10px 0;">' + message + '</div>';
        
        $('.login-error').remove();
        $('#custom-login-form').prepend(errorHtml);
        
        setTimeout(function() {
            $('.login-error').fadeOut();
        }, 5000);
    }
    
    function openNewProjectModal() {
        // Implement new project modal
        alert('New Project modal would open here');
    }
    
    function openFileUploadModal() {
        // Implement file upload modal
        alert('File Upload modal would open here');
    }
    
    function openReportModal() {
        // Implement report generation modal
        alert('Report Generation modal would open here');
    }
    
    function checkNotifications() {
        $.ajax({
            url: ajax_object.ajax_url,
            type: 'POST',
            data: {
                action: 'check_notifications',
                nonce: ajax_object.nonce
            },
            success: function(response) {
                if (response.success && response.data.length > 0) {
                    updateNotifications(response.data);
                }
            }
        });
    }
    
    function updateNotifications(notifications) {
        var notificationList = $('.notification-list');
        
        notifications.forEach(function(notification) {
            var notificationHtml = '<div class="notification-item unread">';
            notificationHtml += '<div class="notification-icon"><img src="' + ajax_object.plugin_url + 'assets/images/alert-icon.png" alt="Alert"></div>';
            notificationHtml += '<div class="notification-content">';
            notificationHtml += '<p>' + notification.message + '</p>';
            notificationHtml += '<span class="notification-time">' + notification.time + '</span>';
            notificationHtml += '</div>';
            notificationHtml += '</div>';
            
            notificationList.prepend(notificationHtml);
        });
        
        // Remove old notifications to keep list manageable
        $('.notification-item').slice(10).remove();
    }
    
    // Initialize tooltips and other UI enhancements
    $('[data-tooltip]').hover(
        function() {
            var tooltip = $('<div class="tooltip">' + $(this).data('tooltip') + '</div>');
            $('body').append(tooltip);
            
            var pos = $(this).offset();
            tooltip.css({
                position: 'absolute',
                top: pos.top - tooltip.outerHeight() - 10,
                left: pos.left + ($(this).outerWidth() / 2) - (tooltip.outerWidth() / 2),
                background: '#333',
                color: 'white',
                padding: '5px 10px',
                borderRadius: '4px',
                fontSize: '12px',
                zIndex: 1000
            });
        },
        function() {
            $('.tooltip').remove();
        }
    );
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        
        var target = $($(this).attr('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });
    
    // Auto-save form data
    $('input, textarea, select').on('change', function() {
        var formId = $(this).closest('form').attr('id');
        if (formId) {
            saveFormData(formId);
        }
    });
    
    function saveFormData(formId) {
        var formData = $('#' + formId).serialize();
        localStorage.setItem('form_' + formId, formData);
    }
    
    function loadFormData(formId) {
        var savedData = localStorage.getItem('form_' + formId);
        if (savedData) {
            var params = new URLSearchParams(savedData);
            params.forEach(function(value, key) {
                $('#' + formId + ' [name="' + key + '"]').val(value);
            });
        }
    }
    
    // Load saved form data on page load
    $('form[id]').each(function() {
        loadFormData($(this).attr('id'));
    });
});

// Password strength indicator
function checkPasswordStrength(password) {
    var strength = 0;
    var feedback = [];
    
    if (password.length >= 8) strength++;
    else feedback.push('At least 8 characters');
    
    if (/[a-z]/.test(password)) strength++;
    else feedback.push('Lowercase letter');
    
    if (/[A-Z]/.test(password)) strength++;
    else feedback.push('Uppercase letter');
    
    if (/[0-9]/.test(password)) strength++;
    else feedback.push('Number');
    
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    else feedback.push('Special character');
    
    return {
        strength: strength,
        feedback: feedback
    };
}