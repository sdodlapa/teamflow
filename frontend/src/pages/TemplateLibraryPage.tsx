import React from 'react';
import { useNavigate } from 'react-router-dom';
import TemplateLibrary from '../components/template-builder/TemplateLibrary';
import { TemplateMetadata } from '../types/template';

export const TemplateLibraryPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSelectTemplate = (template: TemplateMetadata) => {
    console.log('Selected template:', template);
    // TODO: Load template into the builder and navigate there
    // For now, navigate to template builder with template data in state
    navigate('/template-builder', { 
      state: { 
        loadTemplate: template 
      } 
    });
  };

  const handleCreateNew = () => {
    navigate('/template-builder');
  };

  const handleImportTemplate = (template: any) => {
    console.log('Imported template:', template);
    // TODO: Validate and load the imported template
    navigate('/template-builder', { 
      state: { 
        importedTemplate: template 
      } 
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TemplateLibrary
        onSelectTemplate={handleSelectTemplate}
        onCreateNew={handleCreateNew}
        onImportTemplate={handleImportTemplate}
      />
    </div>
  );
};

export default TemplateLibraryPage;