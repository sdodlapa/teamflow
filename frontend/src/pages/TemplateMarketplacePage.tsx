import React from 'react';
import TemplateMarketplace from '../components/template-builder/TemplateMarketplace';

interface MarketplaceTemplate {
  id: string;
  name: string;
  title: string;
  description: string;
  domain_type: string;
  version: string;
  author: {
    name: string;
    avatar: string;
    verified: boolean;
    reputation: number;
  };
  stats: {
    downloads: number;
    likes: number;
    rating: number;
    reviews: number;
    forks: number;
  };
  tags: string[];
  preview_images: string[];
  created_at: string;
  updated_at: string;
  license: string;
  price_type: 'free' | 'premium' | 'enterprise';
  price: number;
  featured: boolean;
  trending: boolean;
  category: string;
  complexity: 'beginner' | 'intermediate' | 'advanced';
  entities_count: number;
  features: string[];
  demo_url?: string;
  github_url?: string;
}

export const TemplateMarketplacePage: React.FC = () => {
  const handleImportTemplate = (template: MarketplaceTemplate) => {
    console.log('Importing template:', template);
    
    // Simulate template import process
    alert(`Template "${template.title}" imported successfully!\n\nThis would redirect to the Template Builder with the imported configuration.`);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TemplateMarketplace
        onImportTemplate={handleImportTemplate}
      />
    </div>
  );
};

export default TemplateMarketplacePage;