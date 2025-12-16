<div class="web-app-search">
    <div class="search-header">
        <h2>Advanced Search</h2>
        <div class="search-hero">
            <!-- PLACE IMAGE: Search hero banner (1200x300px) -->
            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/search-banner.jpg" alt="Advanced Search" class="search-banner">
        </div>
    </div>

    <div class="search-container">
        <form id="advanced-search-form" class="search-form">
            <div class="search-main">
                <div class="search-input-group">
                    <div class="search-icon">
                        <!-- PLACE IMAGE: Search icon (24x24px) -->
                        <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/search-icon.png" alt="Search">
                    </div>
                    <input type="text" id="search-term" name="search_term" placeholder="Enter your search query..." class="search-input">
                    <button type="submit" class="search-btn">
                        <!-- PLACE IMAGE: Search button icon (20x20px) -->
                        <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/search-btn-icon.png" alt="Search">
                        Search
                    </button>
                </div>
            </div>

            <div class="search-filters">
                <h3>Filter Options</h3>
                <div class="filter-grid">
                    <div class="filter-group">
                        <label for="category-filter">
                            <!-- PLACE IMAGE: Category icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/category-icon.png" alt="Category">
                            Category
                        </label>
                        <select id="category-filter" name="filters[category]">
                            <option value="">All Categories</option>
                            <option value="documents">Documents</option>
                            <option value="projects">Projects</option>
                            <option value="reports">Reports</option>
                            <option value="media">Media</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label for="date-filter">
                            <!-- PLACE IMAGE: Calendar icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/calendar-icon.png" alt="Date">
                            Date Range
                        </label>
                        <select id="date-filter" name="filters[date_range]">
                            <option value="">Any Time</option>
                            <option value="today">Today</option>
                            <option value="week">This Week</option>
                            <option value="month">This Month</option>
                            <option value="year">This Year</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label for="status-filter">
                            <!-- PLACE IMAGE: Status icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/status-icon.png" alt="Status">
                            Status
                        </label>
                        <select id="status-filter" name="filters[status]">
                            <option value="">All Status</option>
                            <option value="active">Active</option>
                            <option value="pending">Pending</option>
                            <option value="completed">Completed</option>
                            <option value="archived">Archived</option>
                        </select>
                    </div>

                    <div class="filter-group">
                        <label for="priority-filter">
                            <!-- PLACE IMAGE: Priority icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/priority-icon.png" alt="Priority">
                            Priority
                        </label>
                        <select id="priority-filter" name="filters[priority]">
                            <option value="">All Priorities</option>
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                        </select>
                    </div>
                </div>

                <div class="filter-actions">
                    <button type="button" id="clear-filters" class="btn-secondary">
                        <!-- PLACE IMAGE: Clear icon (16x16px) -->
                        <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/clear-icon.png" alt="Clear">
                        Clear Filters
                    </button>
                    <button type="button" id="save-search" class="btn-tertiary">
                        <!-- PLACE IMAGE: Save icon (16x16px) -->
                        <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/save-icon.png" alt="Save">
                        Save Search
                    </button>
                </div>
            </div>
        </form>

        <div class="search-results">
            <div class="results-header">
                <div class="results-info">
                    <span id="results-count">0 results found</span>
                    <div class="view-options">
                        <button class="view-btn active" data-view="grid">
                            <!-- PLACE IMAGE: Grid view icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/grid-icon.png" alt="Grid View">
                        </button>
                        <button class="view-btn" data-view="list">
                            <!-- PLACE IMAGE: List view icon (20x20px) -->
                            <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/list-icon.png" alt="List View">
                        </button>
                    </div>
                </div>
                
                <div class="sort-options">
                    <label for="sort-by">Sort by:</label>
                    <select id="sort-by" name="sort_by">
                        <option value="relevance">Relevance</option>
                        <option value="date">Date</option>
                        <option value="title">Title</option>
                        <option value="popularity">Popularity</option>
                    </select>
                </div>
            </div>

            <div id="search-results-container" class="results-container grid-view">
                <div class="no-results">
                    <div class="no-results-icon">
                        <!-- PLACE IMAGE: No results illustration (200x200px) -->
                        <img src="<?php echo WAI_PLUGIN_URL; ?>assets/images/no-results.png" alt="No Results">
                    </div>
                    <h3>Start your search</h3>
                    <p>Enter keywords above to find what you're looking for</p>
                </div>
            </div>

            <div class="pagination-container">
                <!-- Pagination will be loaded here -->
            </div>
        </div>
    </div>

    <div class="search-suggestions">
        <h3>Popular Searches</h3>
        <div class="suggestion-tags">
            <span class="suggestion-tag">project reports</span>
            <span class="suggestion-tag">client documents</span>
            <span class="suggestion-tag">meeting notes</span>
            <span class="suggestion-tag">financial data</span>
            <span class="suggestion-tag">user guides</span>
        </div>
    </div>
</div>