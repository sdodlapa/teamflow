# 🏗️ PHASE 2: TEMPLATE EXTRACTION & ENGINE DESIGN
## Section 5: Frontend Component Generation

---

## ⚛️ FRONTEND COMPONENT GENERATION ENGINE

### **React Component Generator**

The frontend generator creates TypeScript React components following TeamFlow's patterns with comprehensive state management, form handling, and API integration.

#### **Component Generator** (`backend/app/core/component_generator.py`)
```python
from typing import Dict, List, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from app.core.domain_config import DomainConfig, EntityConfig

class ComponentGenerator:
    """Generate React TypeScript components from domain configuration"""
    
    def __init__(self, template_dir: Path):
        self.env = Environment(loader=FileSystemLoader(str(template_dir)))
        self.component_template = self.env.get_template('component.tsx.j2')
        self.form_template = self.env.get_template('form.tsx.j2')
        self.list_template = self.env.get_template('list.tsx.j2')
        self.dashboard_template = self.env.get_template('dashboard.tsx.j2')
    
    def generate_main_component(self, entity_name: str, entity_config: EntityConfig, 
                               domain_config: DomainConfig) -> str:
        """Generate main entity management component"""
        
        class_name = entity_name.title()
        camel_name = self._to_camel_case(entity_name)
        plural_name = f"{entity_name}s"
        plural_camel = f"{camel_name}s"
        
        # Extract form fields
        form_fields = self._extract_form_fields(entity_config)
        
        # Extract list display fields
        list_fields = self._extract_list_fields(entity_config)
        
        # Determine component features
        features = self._extract_component_features(entity_config)
        
        return self.component_template.render(
            class_name=class_name,
            camel_name=camel_name,
            plural_name=plural_name,
            plural_camel=plural_camel,
            form_fields=form_fields,
            list_fields=list_fields,
            features=features,
            domain_name=domain_config.domain.name,
            api_endpoint=f"/api/v1/{plural_name}",
            has_search='search' in entity_config.operations,
            has_export='export' in entity_config.operations,
            pagination_default=entity_config.pagination.get('default_limit', 20)
        )
    
    def generate_form_component(self, entity_name: str, entity_config: EntityConfig) -> str:
        """Generate form component for create/edit operations"""
        
        class_name = entity_name.title()
        camel_name = self._to_camel_case(entity_name)
        
        # Process form fields with validation
        form_fields = []
        for field in entity_config.fields:
            field_def = {
                'name': field.name,
                'type': self._map_field_type_to_input(field.type),
                'label': field.description or field.name.replace('_', ' ').title(),
                'required': field.required,
                'validation': self._generate_validation_rules(field),
                'options': field.options if field.type == 'enum' else None,
                'placeholder': field.description or f"Enter {field.name}",
                'default_value': field.default
            }
            form_fields.append(field_def)
        
        return self.form_template.render(
            class_name=class_name,
            camel_name=camel_name,
            form_fields=form_fields,
            has_file_upload=any(f.type == 'file' for f in entity_config.fields)
        )
    
    def generate_list_component(self, entity_name: str, entity_config: EntityConfig) -> str:
        """Generate list/table component with pagination and search"""
        
        class_name = entity_name.title()
        camel_name = self._to_camel_case(entity_name)
        plural_camel = f"{camel_name}s"
        
        # Extract display columns
        columns = []
        for field in entity_config.fields:
            if field.display_in_list:
                column = {
                    'key': field.name,
                    'title': field.description or field.name.replace('_', ' ').title(),
                    'sortable': field.sortable,
                    'searchable': field.searchable,
                    'type': field.type,
                    'format': self._get_display_format(field.type)
                }
                columns.append(column)
        
        # Add action columns
        actions = []
        if 'read' in entity_config.operations:
            actions.append({'name': 'view', 'icon': 'eye', 'color': 'blue'})
        if 'update' in entity_config.operations:
            actions.append({'name': 'edit', 'icon': 'edit', 'color': 'green'})
        if 'delete' in entity_config.operations:
            actions.append({'name': 'delete', 'icon': 'trash', 'color': 'red'})
        
        return self.list_template.render(
            class_name=class_name,
            camel_name=camel_name,
            plural_camel=plural_camel,
            columns=columns,
            actions=actions,
            has_search='search' in entity_config.operations,
            has_filters=entity_config.features.get('advanced_filtering', False),
            pagination_default=entity_config.pagination.get('default_limit', 20)
        )
    
    def _extract_form_fields(self, entity_config: EntityConfig) -> List[Dict]:
        """Extract form field configurations"""
        fields = []
        for field in entity_config.fields:
            if not field.system_field:  # Skip system fields like id, created_at
                fields.append({
                    'name': field.name,
                    'type': self._map_field_type_to_input(field.type),
                    'label': field.description or field.name.replace('_', ' ').title(),
                    'required': field.required,
                    'validation': self._generate_validation_rules(field),
                    'options': field.options if field.type == 'enum' else None
                })
        return fields
    
    def _map_field_type_to_input(self, field_type: str) -> str:
        """Map backend field types to HTML input types"""
        mapping = {
            'string': 'text',
            'text': 'textarea',
            'integer': 'number',
            'decimal': 'number',
            'boolean': 'checkbox',
            'date': 'date',
            'datetime': 'datetime-local',
            'enum': 'select',
            'file': 'file',
            'email': 'email',
            'url': 'url',
            'password': 'password'
        }
        return mapping.get(field_type, 'text')
    
    def _generate_validation_rules(self, field) -> Dict[str, Any]:
        """Generate client-side validation rules"""
        rules = {}
        
        if field.required:
            rules['required'] = True
        
        if field.min_length:
            rules['minLength'] = field.min_length
        
        if field.max_length:
            rules['maxLength'] = field.max_length
        
        if field.min_value is not None:
            rules['min'] = field.min_value
        
        if field.max_value is not None:
            rules['max'] = field.max_value
        
        if field.validation == 'email':
            rules['pattern'] = r'^[^@]+@[^@]+\.[^@]+$'
        elif field.validation == 'positive':
            rules['min'] = 0.01
        
        return rules
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase"""
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
```

#### **Main Component Template** (`templates/frontend/component.tsx.j2`)
```typescript
/**
 * {{ class_name }} Management Component for {{ domain_name }}
 * Auto-generated component with full CRUD operations
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';

import { {{ class_name }}List } from './{{ class_name }}List';
import { {{ class_name }}Form } from './{{ class_name }}Form';
import { {{ class_name }}Detail } from './{{ class_name }}Detail';
import { use{{ class_name }} } from '../hooks/use{{ class_name }}';
import { {{ class_name }}, {{ class_name }}Create, {{ class_name }}Update } from '../types/{{ camel_name }}Types';

export const {{ class_name }}Management: React.FC = () => {
  // State management
  const [selectedItem, setSelectedItem] = useState<{{ class_name }} | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  
  // Snackbar state
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Custom hook for {{ camel_name }} operations
  const {
    {{ plural_camel }},
    loading,
    error,
    create{{ class_name }},
    update{{ class_name }},
    delete{{ class_name }},
    refresh{{ class_name }}s
  } = use{{ class_name }}();

  // Show snackbar notification
  const showNotification = (message: string, severity: 'success' | 'error' | 'warning' | 'info' = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  // Handle create {{ camel_name }}
  const handleCreate = async (data: {{ class_name }}Create) => {
    try {
      await create{{ class_name }}(data);
      setIsCreateDialogOpen(false);
      showNotification('{{ class_name }} created successfully');
      refresh{{ class_name }}s();
    } catch (error) {
      showNotification('Failed to create {{ camel_name }}', 'error');
    }
  };

  // Handle update {{ camel_name }}
  const handleUpdate = async (data: {{ class_name }}Update) => {
    if (!selectedItem) return;
    
    try {
      await update{{ class_name }}(selectedItem.id, data);
      setIsEditDialogOpen(false);
      setSelectedItem(null);
      showNotification('{{ class_name }} updated successfully');
      refresh{{ class_name }}s();
    } catch (error) {
      showNotification('Failed to update {{ camel_name }}', 'error');
    }
  };

  // Handle delete {{ camel_name }}
  const handleDelete = async () => {
    if (!selectedItem) return;
    
    try {
      await delete{{ class_name }}(selectedItem.id);
      setIsDeleteDialogOpen(false);
      setSelectedItem(null);
      showNotification('{{ class_name }} deleted successfully');
      refresh{{ class_name }}s();
    } catch (error) {
      showNotification('Failed to delete {{ camel_name }}', 'error');
    }
  };

  // Handle row actions
  const handleRowAction = (action: string, item: {{ class_name }}) => {
    setSelectedItem(item);
    
    switch (action) {
      case 'view':
        setIsDetailDialogOpen(true);
        break;
      case 'edit':
        setIsEditDialogOpen(true);
        break;
      case 'delete':
        setIsDeleteDialogOpen(true);
        break;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {{ class_name }} Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setIsCreateDialogOpen(true)}
        >
          Add {{ class_name }}
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* {{ class_name }} List */}
      <Card>
        <CardContent>
          <{{ class_name }}List
            {{ plural_camel }}={{ "{{" }} {{ plural_camel }} }}
            loading={{ "{{" }} loading }}
            onRowAction={{ "{{" }} handleRowAction }}
          />
        </CardContent>
      </Card>

      {/* Create Dialog */}
      <Dialog
        open={isCreateDialogOpen}
        onClose={() => setIsCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New {{ class_name }}</DialogTitle>
        <DialogContent>
          <{{ class_name }}Form
            onSubmit={handleCreate}
            loading={loading}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsCreateDialogOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog
        open={isEditDialogOpen}
        onClose={() => setIsEditDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit {{ class_name }}</DialogTitle>
        <DialogContent>
          <{{ class_name }}Form
            initialData={selectedItem}
            onSubmit={handleUpdate}
            loading={loading}
            isEdit
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsEditDialogOpen(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog
        open={isDetailDialogOpen}
        onClose={() => setIsDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{{ class_name }} Details</DialogTitle>
        <DialogContent>
          {selectedItem && (
            <{{ class_name }}Detail {{ camel_name }}={selectedItem} />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDetailDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this {{ camel_name }}? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleDelete} 
            color="error" 
            variant="contained"
            disabled={loading}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert
          severity={snackbar.severity}
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};
```

#### **Form Component Template** (`templates/frontend/form.tsx.j2`)
```typescript
/**
 * {{ class_name }} Form Component
 * Auto-generated form with validation and submission handling
 */

import React from 'react';
import {
  Box,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  FormControlLabel,
  Checkbox,
  Button,
  Grid,
  FormHelperText
} from '@mui/material';
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

import { {{ class_name }}Create, {{ class_name }}Update, {{ class_name }} } from '../types/{{ camel_name }}Types';

// Validation schema
const validationSchema = yup.object().shape({
  {% for field in form_fields %}
  {{ field.name }}: yup
    {% if field.type == 'text' or field.type == 'textarea' %}
    .string()
    {% if field.required %}.required('{{ field.label }} is required'){% endif %}
    {% if field.validation.minLength %}.min({{ field.validation.minLength }}, 'Minimum {{ field.validation.minLength }} characters'){% endif %}
    {% if field.validation.maxLength %}.max({{ field.validation.maxLength }}, 'Maximum {{ field.validation.maxLength }} characters'){% endif %}
    {% elif field.type == 'number' %}
    .number()
    {% if field.required %}.required('{{ field.label }} is required'){% endif %}
    {% if field.validation.min is defined %}.min({{ field.validation.min }}, 'Minimum value is {{ field.validation.min }}'){% endif %}
    {% if field.validation.max is defined %}.max({{ field.validation.max }}, 'Maximum value is {{ field.validation.max }}'){% endif %}
    {% elif field.type == 'email' %}
    .string()
    .email('Invalid email format')
    {% if field.required %}.required('{{ field.label }} is required'){% endif %}
    {% elif field.type == 'checkbox' %}
    .boolean()
    {% else %}
    .string()
    {% if field.required %}.required('{{ field.label }} is required'){% endif %}
    {% endif %}
    ,
  {% endfor %}
});

interface {{ class_name }}FormProps {
  initialData?: Partial<{{ class_name }}>;
  onSubmit: (data: {{ class_name }}Create | {{ class_name }}Update) => Promise<void>;
  loading?: boolean;
  isEdit?: boolean;
}

export const {{ class_name }}Form: React.FC<{{ class_name }}FormProps> = ({
  initialData,
  onSubmit,
  loading = false,
  isEdit = false
}) => {
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting }
  } = useForm({
    resolver: yupResolver(validationSchema),
    defaultValues: initialData || {}
  });

  const handleFormSubmit = async (data: any) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit(handleFormSubmit)} sx={{ mt: 2 }}>
      <Grid container spacing={3}>
        {% for field in form_fields %}
        <Grid item xs={12} {% if field.type != 'textarea' %}md={6}{% endif %}>
          {% if field.type == 'text' or field.type == 'email' or field.type == 'url' or field.type == 'password' %}
          <Controller
            name="{{ field.name }}"
            control={control}
            render={({ field: formField }) => (
              <TextField
                {...formField}
                label="{{ field.label }}"
                type="{{ field.type }}"
                fullWidth
                error={!!errors.{{ field.name }}}
                helperText={errors.{{ field.name }}?.message}
                required={{ "{{" }} {{ field.required | lower }} }}
                placeholder="{{ field.placeholder or '' }}"
              />
            )}
          />
          
          {% elif field.type == 'textarea' %}
          <Controller
            name="{{ field.name }}"
            control={control}
            render={({ field: formField }) => (
              <TextField
                {...formField}
                label="{{ field.label }}"
                multiline
                rows={4}
                fullWidth
                error={!!errors.{{ field.name }}}
                helperText={errors.{{ field.name }}?.message}
                required={{ "{{" }} {{ field.required | lower }} }}
                placeholder="{{ field.placeholder or '' }}"
              />
            )}
          />
          
          {% elif field.type == 'number' %}
          <Controller
            name="{{ field.name }}"
            control={control}
            render={({ field: formField }) => (
              <TextField
                {...formField}
                label="{{ field.label }}"
                type="number"
                fullWidth
                error={!!errors.{{ field.name }}}
                helperText={errors.{{ field.name }}?.message}
                required={{ "{{" }} {{ field.required | lower }} }}
                {% if field.validation.min is defined %}
                inputProps={{ "{{" }} min: {{ field.validation.min }} }}
                {% endif %}
                {% if field.validation.max is defined %}
                inputProps={{ "{{" }} ...inputProps, max: {{ field.validation.max }} }}
                {% endif %}
              />
            )}
          />
          
          {% elif field.type == 'select' %}
          <FormControl fullWidth error={!!errors.{{ field.name }}}>
            <InputLabel>{{ field.label }}</InputLabel>
            <Controller
              name="{{ field.name }}"
              control={control}
              render={({ field: formField }) => (
                <Select
                  {...formField}
                  label="{{ field.label }}"
                  required={{ "{{" }} {{ field.required | lower }} }}
                >
                  {% if field.options %}
                  {% for option in field.options %}
                  <MenuItem value="{{ option }}">{{ option.replace('_', ' ').title() }}</MenuItem>
                  {% endfor %}
                  {% endif %}
                </Select>
              )}
            />
            {errors.{{ field.name }} && (
              <FormHelperText>{errors.{{ field.name }}?.message}</FormHelperText>
            )}
          </FormControl>
          
          {% elif field.type == 'checkbox' %}
          <Controller
            name="{{ field.name }}"
            control={control}
            render={({ field: formField }) => (
              <FormControlLabel
                control={
                  <Checkbox
                    {...formField}
                    checked={formField.value || false}
                  />
                }
                label="{{ field.label }}"
              />
            )}
          />
          
          {% elif field.type == 'date' or field.type == 'datetime-local' %}
          <Controller
            name="{{ field.name }}"
            control={control}
            render={({ field: formField }) => (
              <TextField
                {...formField}
                label="{{ field.label }}"
                type="{{ field.type }}"
                fullWidth
                error={!!errors.{{ field.name }}}
                helperText={errors.{{ field.name }}?.message}
                required={{ "{{" }} {{ field.required | lower }} }}
                InputLabelProps={{
                  shrink: true,
                }}
              />
            )}
          />
          {% endif %}
        </Grid>
        {% endfor %}
        
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
            <Button
              type="submit"
              variant="contained"
              disabled={isSubmitting || loading}
            >
              {isEdit ? 'Update' : 'Create'} {{ class_name }}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};
```

### **Custom Hooks Generation**

#### **API Hook Template** (`templates/frontend/hooks/useEntity.ts.j2`)
```typescript
/**
 * {{ class_name }} API Hook
 * Auto-generated custom hook for {{ camel_name }} operations
 */

import { useState, useEffect, useCallback } from 'react';
import { {{ class_name }}, {{ class_name }}Create, {{ class_name }}Update, {{ class_name }}List } from '../types/{{ camel_name }}Types';
import { apiClient } from '../utils/apiClient';

interface Use{{ class_name }}Return {
  {{ plural_camel }}: {{ class_name }}[];
  {{ camel_name }}List: {{ class_name }}List | null;
  loading: boolean;
  error: string | null;
  create{{ class_name }}: (data: {{ class_name }}Create) => Promise<{{ class_name }}>;
  update{{ class_name }}: (id: number, data: {{ class_name }}Update) => Promise<{{ class_name }}>;
  delete{{ class_name }}: (id: number) => Promise<void>;
  get{{ class_name }}: (id: number) => Promise<{{ class_name }}>;
  refresh{{ class_name }}s: () => Promise<void>;
  search{{ class_name }}s: (query: string) => Promise<void>;
}

export const use{{ class_name }} = (): Use{{ class_name }}Return => {
  const [{{ plural_camel }}, set{{ plural_camel.title() }}] = useState<{{ class_name }}[]>([]);
  const [{{ camel_name }}List, set{{ class_name }}List] = useState<{{ class_name }}List | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch {{ plural_camel }} with pagination
  const fetch{{ plural_camel.title() }} = useCallback(async (skip = 0, limit = {{ pagination_default }}) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get<{{ class_name }}List>('{{ api_endpoint }}', {
        params: { skip, limit }
      });
      
      set{{ class_name }}List(response.data);
      set{{ plural_camel.title() }}(response.data.items);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to fetch {{ plural_camel }}');
    } finally {
      setLoading(false);
    }
  }, []);

  // Create {{ camel_name }}
  const create{{ class_name }} = useCallback(async (data: {{ class_name }}Create): Promise<{{ class_name }}> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.post<{{ class_name }}>('{{ api_endpoint }}', data);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create {{ camel_name }}';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // Update {{ camel_name }}
  const update{{ class_name }} = useCallback(async (id: number, data: {{ class_name }}Update): Promise<{{ class_name }}> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.put<{{ class_name }}>(`{{ api_endpoint }}/${id}`, data);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to update {{ camel_name }}';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // Delete {{ camel_name }}
  const delete{{ class_name }} = useCallback(async (id: number): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      await apiClient.delete(`{{ api_endpoint }}/${id}`);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete {{ camel_name }}';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // Get single {{ camel_name }}
  const get{{ class_name }} = useCallback(async (id: number): Promise<{{ class_name }}> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get<{{ class_name }}>(`{{ api_endpoint }}/${id}`);
      return response.data;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to fetch {{ camel_name }}';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  // Refresh {{ plural_camel }} list
  const refresh{{ class_name }}s = useCallback(async () => {
    await fetch{{ plural_camel.title() }}();
  }, [fetch{{ plural_camel.title() }}]);

  {% if has_search %}
  // Search {{ plural_camel }}
  const search{{ class_name }}s = useCallback(async (query: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get<{{ class_name }}List>('{{ api_endpoint }}/search', {
        params: { q: query }
      });
      
      set{{ class_name }}List(response.data);
      set{{ plural_camel.title() }}(response.data.items);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to search {{ plural_camel }}');
    } finally {
      setLoading(false);
    }
  }, []);
  {% else %}
  const search{{ class_name }}s = useCallback(async (query: string) => {
    // Search not implemented for this entity
    console.warn('Search not implemented for {{ class_name }}');
  }, []);
  {% endif %}

  // Initial load
  useEffect(() => {
    fetch{{ plural_camel.title() }}();
  }, [fetch{{ plural_camel.title() }}]);

  return {
    {{ plural_camel }},
    {{ camel_name }}List,
    loading,
    error,
    create{{ class_name }},
    update{{ class_name }},
    delete{{ class_name }},
    get{{ class_name }},
    refresh{{ class_name }}s,
    search{{ class_name }}s
  };
};
```

---

*Continue to Section 6: Validation & Testing Framework...*