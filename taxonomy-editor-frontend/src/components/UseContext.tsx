import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define types for the context
interface AppContextType {
  taxonomyName: string;
  setTaxonomyName: (value: string) => void;
  ownerName: string;
  setOwnerName: (value: string) => void;
  description: string;
  setDescription: (value: string) => void;
  clearContext: () => void; // Correct return type here
}

// Create the context with default values
const AppContext = createContext<AppContextType | undefined>(undefined);

// Create a provider component
export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [taxonomyName, setTaxonomyName] = useState("");
  const [ownerName, setOwnerName] = useState("");
  const [description, setDescription] = useState("");

  const clearContext = () => {
    setTaxonomyName("");
    setOwnerName("");
    setDescription("");
  };

  return (
    <AppContext.Provider
      value={{
        taxonomyName,
        setTaxonomyName,
        ownerName,
        setOwnerName,
        description,
        setDescription,
        clearContext,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

// Create a custom hook to use the context
export const useAppContext = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};
