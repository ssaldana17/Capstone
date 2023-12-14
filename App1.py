import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Map</title>
    <script src="https://api.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.6.1/mapbox-gl.css" rel="stylesheet" />
    <style>
        body { margin: 0; padding: 0; }
        #map { position: absolute; top: 0; bottom: 0; height: 100vh; width: calc(100% - 250px); right: 0; }
        #sidebar { position: absolute; width: 250px; height: 100%; top: 0; left: 0; overflow-y: auto; background-color: white; font-family: 'Calibri', sans-serif; font-size: 12px;}
        ul { list-style-type: none; padding: 0px; }
        li { margin: 10px; cursor: pointer; }
        li:hover { font-weight: bold; background-color: #e9e9e9}
    </style>
</head>
<body>
      <div id="sidebar">
        <h3>Filters</h3>
        <div>
            <label for="category-filter">Category:</label>
            <select id="category-filter">
                <option value="all">All Categories</option>
                <option value="Crime">Crime</option>
                <option value="Education">Education</option>
                <option value="Finance and Buisness">Finance and Buisness</option>
                <option value="Media">Media</option>
                <option value="Personal and Relationships">Personal and Relationships</option>
                <option value="Politics">Politics</option>
                <option value="Religion">Politics</option>
                <option value="Trauma">Trauma</option>
            </select>
        </div>
        <div>
            <label for="date-filter">Date Range:</label>
            <select id="date-filter">
                <option value="all">All Time</option>
                <option value="30days">Past 30 Days</option>
                <option value="3months">Past 3 Months</option>
                <option value="3months">Past 6 Months</option>
                <option value="3months">Past Year</option>
                <option value="custom">Custom Date Range</option>
            </select>
        </div>
        <div id="custom-date-range" style="display: none;">
          <label for="start-date">Start Date:</label>
          <input type="date" id="start-date">
          <label for="end-date">End Date:</label>
          <input type="date" id="end-date">
      </div>
        <h3>Article Titles</h3>
        <ul id="article-list"></ul>
    </div>
    <div id="map"></div>
    <script>
        mapboxgl.accessToken = 'pk.eyJ1IjoicmZ1a3V0b2t1IiwiYSI6ImNsb2h2dW93NzE1OGcycXJyZ2FvY3I4aXMifQ.zFL4aMOTQT9u-eWd6oFsVA';

        const map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v11',
            center: [-96, 37.8],
            zoom: 3
        });

        let allArticles = [];

        map.on('load', () => {
            map.addSource('your-data-source', {
                type: 'geojson',
                data: 'https://raw.githubusercontent.com/ssaldana17/Capstone/main/Output_GeoJSON_3.geojson'
            });

            // Layer for the epicenter
            map.addLayer({
                id: 'epicenter-layer',
                type: 'circle',
                source: 'your-data-source',
                filter: ['==', ['get', 'IsEpicenterPresent'], true],
                paint: {
                    'circle-color': 'red',
                    'circle-radius': 8,
                    'circle-opacity': 0.8
                }
            });

            // Layer for correlated locations
            map.addLayer({
                id: 'correlated-locations-layer',
                type: 'circle',
                source: 'your-data-source',
                filter: ['==', ['get', 'IsEpicenterPresent'], false],
                paint: {
                    'circle-color': 'blue',
                    'circle-radius': 14,
                    'circle-opacity': 0.5
                }
            });
        });

        function filterArticlesByCategory(articles, selectedCategory) {
            return selectedCategory === 'all' ? articles : articles.filter(article => article.category === selectedCategory);
        }

        function filterArticlesByDateRange(articles, selectedDateRange) {
            const now = new Date();
            return articles.filter(article => {
                const articleDate = new Date(article.date);
                switch (selectedDateRange) {
                    case '30days': return now - articleDate <= 30 * 24 * 60 * 60 * 1000;
                    case '3months': return now - articleDate <= 3 * 30 * 24 * 60 * 60 * 1000;
                    case '6months': return now - articleDate <= 6 * 30 * 24 * 60 * 60 * 1000;
                    case '3months': return now - articleDate <= 3 * 30 * 24 * 60 * 60 * 1000;
                    case '1year': return now - articleDate <= 12 * 30 * 24 * 60 * 60 * 1000; // Last year
                    case 'all': return true; // All time
                    default: return true;
                }
            });
        }

        function filterArticlesByCustomDateRange(articles, startDate, endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            return articles.filter(article => {
                const articleDate = new Date(article.date);
                return articleDate >= start && articleDate <= end;
            });
        }

        function updateArticleList(articles) {
            const articleList = document.getElementById('article-list');
            articleList.innerHTML = '';
            articles.forEach(article => {
                const listItem = document.createElement('li');
                listItem.textContent = article.title;
                listItem.onclick = function() {
                    selectArticle(article);
                };
                articleList.appendChild(listItem);
            });
        }

        document.addEventListener('DOMContentLoaded', function () {
            fetch('https://raw.githubusercontent.com/ssaldana17/Capstone/main/Output_GeoJSON_3.geojson')
            .then(response => response.json())
            .then(data => {
                allArticles = data.features.map(feature => {
                    return {
                        title: feature.properties['Article Title'],
                        date: feature.properties['Date'],
                        category: feature.properties['Category'],
                        isEpicenterPresent: feature.properties.IsEpicenterPresent,
                        coordinates: feature.geometry.coordinates,
                        locationNames: feature.properties.LocationNames
                    };
                });
                updateArticleList(allArticles);
            });

            document.getElementById('category-filter').addEventListener('change', applyFilters);
            document.getElementById('date-filter').addEventListener('change', function() {
                const selectedDateRange = this.value;

                const customDateRangeDiv = document.getElementById('custom-date-range');
                if (selectedDateRange === 'custom') {
                    customDateRangeDiv.style.display = 'block';
                } else {
                    customDateRangeDiv.style.display = 'none';
                    applyFilters(); // Apply filters when a predefined range is selected
                }
            });
            
            document.getElementById('start-date').addEventListener('change', applyFilters);
            document.getElementById('end-date').addEventListener('change', applyFilters);

            function applyFilters() {
              const selectedCategory = document.getElementById('category-filter').value;
              const selectedDateRange = document.getElementById('date-filter').value;

              let filteredArticles = filterArticlesByCategory(allArticles, selectedCategory);

              if (selectedDateRange === 'custom') {
                  const startDate = document.getElementById('start-date').value;
                  const endDate = document.getElementById('end-date').value;
                  if (startDate && endDate) {
                      filteredArticles = filterArticlesByCustomDateRange(filteredArticles, startDate, endDate);
                  }
              } else {
                  filteredArticles = filterArticlesByDateRange(filteredArticles, selectedDateRange);
              }
              updateArticleList(filteredArticles);
          }

        });

        function selectArticle(article) {
            let features = [];

            if (article.coordinates) {
              article.coordinates.forEach((coord, index) => {
                  const isEpicenter = article.isEpicenterPresent && index === 0;
                  features.push({
                      type: 'Feature',
                      properties: { IsEpicenterPresent: isEpicenter },
                      geometry: {
                          type: 'Point',
                          coordinates: coord
                      }
                  });
              });
          }

            map.getSource('your-data-source').setData({
                type: 'FeatureCollection',
                features: features
            });

            map.setLayoutProperty('correlated-locations-layer', 'visibility', 'visible');
            if (article.isEpicenterPresent) {
                map.setLayoutProperty('epicenter-layer', 'visibility', 'visible');
            } else {
                map.setLayoutProperty('epicenter-layer', 'visibility', 'none');
            }
        }

    </script>
</body>
</html>
"""

# Embed the HTML in Streamlit
components.html(html_content, height=1000, scrolling=True)
