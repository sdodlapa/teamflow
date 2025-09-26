/**
 * Template Builder - Day 17 Implementation
 * Drag-and-drop template creation interface with real-time preview
 */

import React, { useState, useCallback } from 'react';
import { 
  Plus, 
  Grid, 
  Type, 
  Image, 
  List, 
  Calendar,
  CheckSquare,
  FileText,
  Save,
  Eye,
  Code,
  Trash2,
  Move,
  Copy
} from 'lucide-react';
import { DndProvider, useDrag, useDrop, DropTargetMonitor } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import ErrorBoundary from './ErrorBoundary';
import { renderTemplateComponent } from './TemplateComponentLibrary';
import SaveTemplateDialog from './SaveTemplateDialog';
import uiTemplateService, { SaveUITemplateRequest } from '../services/uiTemplateService';

// Template component types
export interface TemplateComponent {
  id: string;
  type: ComponentType;
  props: Record<string, any>;
  children?: TemplateComponent[];
  position: { x: number; y: number };
  size: { width: number; height: number };
}

export type ComponentType = 
  | 'text'
  | 'heading' 
  | 'image'
  | 'button'
  | 'input'
  | 'textarea'
  | 'select'
  | 'checkbox'
  | 'date'
  | 'list'
  | 'table'
  | 'card'
  | 'section'
  | 'grid';

// Component library data
const COMPONENT_LIBRARY: Array<{
  type: ComponentType;
  label: string;
  icon: React.ComponentType<any>;
  category: string;
  defaultProps: Record<string, any>;
}> = [
  // Text Components
  { type: 'heading', label: 'Heading', icon: Type, category: 'Text', defaultProps: { level: 1, text: 'Heading' } },
  { type: 'text', label: 'Text', icon: FileText, category: 'Text', defaultProps: { content: 'Text content' } },
  
  // Input Components
  { type: 'input', label: 'Text Input', icon: Type, category: 'Form', defaultProps: { placeholder: 'Enter text...', label: 'Text Field' } },
  { type: 'textarea', label: 'Text Area', icon: FileText, category: 'Form', defaultProps: { placeholder: 'Enter description...', label: 'Description' } },
  { type: 'select', label: 'Dropdown', icon: List, category: 'Form', defaultProps: { options: ['Option 1', 'Option 2'], label: 'Select Option' } },
  { type: 'checkbox', label: 'Checkbox', icon: CheckSquare, category: 'Form', defaultProps: { label: 'Check this option' } },
  { type: 'date', label: 'Date Picker', icon: Calendar, category: 'Form', defaultProps: { label: 'Select Date' } },
  { type: 'button', label: 'Button', icon: Plus, category: 'Form', defaultProps: { text: 'Button', variant: 'primary' } },
  
  // Media Components
  { type: 'image', label: 'Image', icon: Image, category: 'Media', defaultProps: { alt: 'Image', src: '/api/placeholder/300/200' } },
  
  // Layout Components
  { type: 'section', label: 'Section', icon: Grid, category: 'Layout', defaultProps: { title: 'Section Title' } },
  { type: 'card', label: 'Card', icon: FileText, category: 'Layout', defaultProps: { title: 'Card Title', content: 'Card content' } },
  { type: 'grid', label: 'Grid', icon: Grid, category: 'Layout', defaultProps: { columns: 2 } },
  { type: 'list', label: 'List', icon: List, category: 'Layout', defaultProps: { items: ['Item 1', 'Item 2', 'Item 3'] } },
  { type: 'table', label: 'Table', icon: Grid, category: 'Layout', defaultProps: { headers: ['Column 1', 'Column 2'], rows: [['Data 1', 'Data 2']] } },
];

// Drag and drop types
const ItemTypes = {
  COMPONENT: 'component',
  TEMPLATE_COMPONENT: 'template_component',
};

// Component Library Panel
const ComponentLibrary: React.FC<{ onAddComponent: (component: any) => void }> = ({ 
  onAddComponent 
}) => {
  const categories = Array.from(new Set(COMPONENT_LIBRARY.map(c => c.category)));

  return (
    <div className="w-80 bg-white border-r border-gray-200 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Component Library</h2>
      
      {categories.map(category => (
        <div key={category} className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2 uppercase tracking-wide">
            {category}
          </h3>
          <div className="space-y-2">
            {COMPONENT_LIBRARY.filter(c => c.category === category).map(component => (
              <DraggableComponent
                key={component.type}
                component={component}
                onAdd={() => onAddComponent(component)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

// Draggable component from library
const DraggableComponent: React.FC<{
  component: any;
  onAdd: () => void;
}> = ({ component, onAdd }) => {
  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.COMPONENT,
    item: { ...component },
    collect: (monitor: any) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const Icon = component.icon;

  return (
    <div
      ref={drag}
      onClick={onAdd}
      className={`
        flex items-center p-3 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer
        hover:bg-gray-100 hover:border-gray-300 transition-colors
        ${isDragging ? 'opacity-50' : 'opacity-100'}
      `}
    >
      <Icon className="h-4 w-4 text-gray-600 mr-3" />
      <span className="text-sm text-gray-800">{component.label}</span>
    </div>
  );
};

// Template Canvas
const TemplateCanvas: React.FC<{
  components: TemplateComponent[];
  selectedComponent: string | null;
  onSelectComponent: (id: string | null) => void;
  onUpdateComponent: (id: string, updates: Partial<TemplateComponent>) => void;
  onDeleteComponent: (id: string) => void;
  onAddComponent: (component: TemplateComponent) => void;
}> = ({ 
  components, 
  selectedComponent, 
  onSelectComponent, 
  onUpdateComponent, 
  onDeleteComponent,
  onAddComponent 
}) => {
  const [{ isOver }, drop] = useDrop({
    accept: ItemTypes.COMPONENT,
    drop: (item: any, monitor: DropTargetMonitor) => {
      if (!monitor.didDrop()) {
        const clientOffset = monitor.getClientOffset();
        if (clientOffset) {
          const newComponent: TemplateComponent = {
            id: `${item.type}_${Date.now()}`,
            type: item.type,
            props: { ...item.defaultProps },
            position: { x: clientOffset.x, y: clientOffset.y },
            size: { width: 300, height: 100 },
          };
          onAddComponent(newComponent);
        }
      }
    },
    collect: (monitor: any) => ({
      isOver: monitor.isOver(),
    }),
  });

  return (
    <div 
      ref={drop}
      className={`
        flex-1 bg-gray-50 relative min-h-screen p-8 overflow-auto
        ${isOver ? 'bg-blue-50 border-2 border-blue-300 border-dashed' : ''}
      `}
    >
      {components.length === 0 ? (
        <div className="flex items-center justify-center h-96 text-gray-500">
          <div className="text-center">
            <Grid className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-lg font-medium">Start building your template</p>
            <p className="text-sm">Drag components from the library or click to add them</p>
          </div>
        </div>
      ) : (
        components.map(component => (
          <TemplateComponentRenderer
            key={component.id}
            component={component}
            isSelected={selectedComponent === component.id}
            onSelect={() => onSelectComponent(component.id)}
            onUpdate={(updates) => onUpdateComponent(component.id, updates)}
            onDelete={() => onDeleteComponent(component.id)}
          />
        ))
      )}
    </div>
  );
};

// Template component renderer
const TemplateComponentRenderer: React.FC<{
  component: TemplateComponent;
  isSelected: boolean;
  onSelect: () => void;
  onUpdate: (updates: Partial<TemplateComponent>) => void;
  onDelete: () => void;
}> = ({ component, isSelected, onSelect, onDelete }) => {
  const [{ isDragging }, drag] = useDrag({
    type: ItemTypes.TEMPLATE_COMPONENT,
    item: { id: component.id },
    collect: (monitor: any) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const renderComponent = () => {
    return renderTemplateComponent(component);
  };

  return (
    <div
      ref={drag}
      onClick={onSelect}
      style={{
        position: 'absolute',
        left: component.position.x,
        top: component.position.y,
        width: component.size.width,
        minHeight: component.size.height,
      }}
      className={`
        cursor-pointer transition-all duration-200
        ${isDragging ? 'opacity-50' : 'opacity-100'}
        ${isSelected ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
      `}
    >
      {renderComponent()}
      
      {isSelected && (
        <div className="absolute -top-8 -right-8 flex space-x-1">
          <button
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Implement move/resize handles
            }}
            className="p-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
          >
            <Move className="h-3 w-3" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              // TODO: Implement copy functionality
            }}
            className="p-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700"
          >
            <Copy className="h-3 w-3" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="p-1 bg-red-600 text-white rounded text-xs hover:bg-red-700"
          >
            <Trash2 className="h-3 w-3" />
          </button>
        </div>
      )}
    </div>
  );
};

// Properties Panel
const PropertiesPanel: React.FC<{
  selectedComponent: TemplateComponent | null;
  onUpdateComponent: (updates: Partial<TemplateComponent>) => void;
}> = ({ selectedComponent, onUpdateComponent }) => {
  if (!selectedComponent) {
    return (
      <div className="w-80 bg-white border-l border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Properties</h2>
        <p className="text-gray-500 text-sm">Select a component to edit its properties</p>
      </div>
    );
  }

  const handlePropsUpdate = (key: string, value: any) => {
    onUpdateComponent({
      props: { ...selectedComponent.props, [key]: value }
    });
  };

  const renderPropertyEditor = () => {
    switch (selectedComponent.type) {
      case 'heading':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Text</label>
              <input
                type="text"
                value={selectedComponent.props.text || ''}
                onChange={(e) => handlePropsUpdate('text', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Level</label>
              <select
                value={selectedComponent.props.level || 1}
                onChange={(e) => handlePropsUpdate('level', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={1}>H1</option>
                <option value={2}>H2</option>
                <option value={3}>H3</option>
              </select>
            </div>
          </div>
        );
        
      case 'button':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Text</label>
              <input
                type="text"
                value={selectedComponent.props.text || ''}
                onChange={(e) => handlePropsUpdate('text', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Variant</label>
              <select
                value={selectedComponent.props.variant || 'primary'}
                onChange={(e) => handlePropsUpdate('variant', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="primary">Primary</option>
                <option value="secondary">Secondary</option>
                <option value="outline">Outline</option>
              </select>
            </div>
          </div>
        );
        
      default:
        return (
          <div className="space-y-4">
            <p className="text-sm text-gray-500">No properties available for this component type</p>
          </div>
        );
    }
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 p-4 overflow-y-auto">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Properties</h2>
      
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Component Type</h3>
        <p className="text-sm text-gray-500 capitalize">{selectedComponent.type}</p>
      </div>
      
      {renderPropertyEditor()}
      
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Position & Size</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div>
            <label className="block text-gray-500 mb-1">X</label>
            <input
              type="number"
              value={selectedComponent.position.x}
              onChange={(e) => onUpdateComponent({
                position: { ...selectedComponent.position, x: parseInt(e.target.value) }
              })}
              className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
            />
          </div>
          <div>
            <label className="block text-gray-500 mb-1">Y</label>
            <input
              type="number"
              value={selectedComponent.position.y}
              onChange={(e) => onUpdateComponent({
                position: { ...selectedComponent.position, y: parseInt(e.target.value) }
              })}
              className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
            />
          </div>
          <div>
            <label className="block text-gray-500 mb-1">Width</label>
            <input
              type="number"
              value={selectedComponent.size.width}
              onChange={(e) => onUpdateComponent({
                size: { ...selectedComponent.size, width: parseInt(e.target.value) }
              })}
              className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
            />
          </div>
          <div>
            <label className="block text-gray-500 mb-1">Height</label>
            <input
              type="number"
              value={selectedComponent.size.height}
              onChange={(e) => onUpdateComponent({
                size: { ...selectedComponent.size, height: parseInt(e.target.value) }
              })}
              className="w-full px-2 py-1 border border-gray-300 rounded text-xs"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Template Builder
const TemplateBuilder: React.FC = () => {
  const [components, setComponents] = useState<TemplateComponent[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);
  const [templateName, setTemplateName] = useState('Untitled Template');
  const [previewMode, setPreviewMode] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleAddComponent = useCallback((libraryComponent: any) => {
    const newComponent: TemplateComponent = {
      id: `${libraryComponent.type}_${Date.now()}`,
      type: libraryComponent.type,
      props: { ...libraryComponent.defaultProps },
      position: { x: 100 + Math.random() * 200, y: 100 + Math.random() * 200 },
      size: { width: 300, height: 100 },
    };
    setComponents(prev => [...prev, newComponent]);
    setSelectedComponent(newComponent.id);
  }, []);

  const handleUpdateComponent = useCallback((id: string, updates: Partial<TemplateComponent>) => {
    setComponents(prev => prev.map(comp => 
      comp.id === id ? { ...comp, ...updates } : comp
    ));
  }, []);

  const handleDeleteComponent = useCallback((id: string) => {
    setComponents(prev => prev.filter(comp => comp.id !== id));
    if (selectedComponent === id) {
      setSelectedComponent(null);
    }
  }, [selectedComponent]);

  const handleSaveTemplate = useCallback(async (templateData: SaveUITemplateRequest) => {
    try {
      // Try saving to backend first
      try {
        const savedTemplate = await uiTemplateService.saveUITemplate(templateData);
        setSaveMessage({ type: 'success', text: `Template "${savedTemplate.name}" saved successfully!` });
      } catch (apiError) {
        // Fallback to local storage if API is not available
        console.warn('API save failed, using local storage:', apiError);
        uiTemplateService.saveToLocalStorage({
          ...templateData,
          id: Date.now().toString()
        });
        setSaveMessage({ type: 'success', text: `Template "${templateData.name}" saved locally!` });
      }

      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      console.error('Error saving template:', error);
      setSaveMessage({ type: 'error', text: 'Error saving template. Please try again.' });
      setTimeout(() => setSaveMessage(null), 3000);
    }
  }, []);

  const openSaveDialog = useCallback(() => {
    setShowSaveDialog(true);
  }, []);

  const selectedComponentData = components.find(comp => comp.id === selectedComponent);

  if (previewMode) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">Template Preview</h1>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setPreviewMode(false)}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              <Code className="h-4 w-4 mr-2 inline" />
              Edit
            </button>
          </div>
        </div>
        <div className="p-8">
          {components.map(component => (
            <div
              key={component.id}
              style={{
                position: 'absolute',
                left: component.position.x,
                top: component.position.y + 100, // Offset for header
                width: component.size.width,
                minHeight: component.size.height,
              }}
            >
              <TemplateComponentRenderer
                component={component}
                isSelected={false}
                onSelect={() => {}}
                onUpdate={() => {}}
                onDelete={() => {}}
              />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <ErrorBoundary level="page" showDetails={import.meta.env.DEV}>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <input
                type="text"
                value={templateName}
                onChange={(e) => setTemplateName(e.target.value)}
                className="text-xl font-semibold text-gray-900 bg-transparent border-none focus:outline-none focus:bg-gray-50 px-2 py-1 rounded"
              />
              <span className="text-sm text-gray-500">
                {components.length} component{components.length !== 1 ? 's' : ''}
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setPreviewMode(true)}
                className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </button>
              <button
                onClick={openSaveDialog}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Save className="h-4 w-4 mr-2" />
                Save Template
              </button>
            </div>
          </div>
          
          {/* Main Content */}
          <div className="flex flex-1 overflow-hidden">
            <ComponentLibrary onAddComponent={handleAddComponent} />
            
            <TemplateCanvas
              components={components}
              selectedComponent={selectedComponent}
              onSelectComponent={setSelectedComponent}
              onUpdateComponent={handleUpdateComponent}
              onDeleteComponent={handleDeleteComponent}
              onAddComponent={handleAddComponent}
            />
            
            <PropertiesPanel
              selectedComponent={selectedComponentData || null}
              onUpdateComponent={(updates) => 
                selectedComponent && handleUpdateComponent(selectedComponent, updates)
              }
            />
          </div>

          {/* Save Template Dialog */}
          <SaveTemplateDialog
            isOpen={showSaveDialog}
            onClose={() => setShowSaveDialog(false)}
            onSave={handleSaveTemplate}
            components={components}
            initialData={{
              name: templateName !== 'Untitled Template' ? templateName : '',
              category: 'general',
              is_public: false
            }}
          />

          {/* Save Message */}
          {saveMessage && (
            <div className={`fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
              saveMessage.type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' : 'bg-red-100 text-red-800 border border-red-200'
            }`}>
              {saveMessage.text}
            </div>
          )}
        </div>
      </ErrorBoundary>
    </DndProvider>
  );
};

export default TemplateBuilder;