import { createContext, useContext, useState } from "react";

const ScoreContext = createContext();

export function ScoreProvider({ children }) {
  const [currentContext, setCurrentContext] = useState(null);

  return (
    <ScoreContext.Provider value={{ currentContext, setCurrentContext }}>
      {children}
    </ScoreContext.Provider>
  );
}

export function useScoreContext() {
  return useContext(ScoreContext);
}
