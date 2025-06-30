# Documentation: {{ file_name }}

## Documentation

{{ documentation }}

{% if architecture_description and include_architecture %}
## Architecture Analysis

{{ architecture_description }}
{% endif %}
