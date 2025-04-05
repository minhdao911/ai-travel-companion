import type { TravelContext, TravelPreferences } from "@/types";
import { defineStore } from "pinia";

export const useTravelStore = defineStore("travel", {
  state: () => ({
    preferences: null as TravelPreferences | null,
    context: null as TravelContext | null,
  }),
  actions: {
    setPreferences(preferences: Partial<TravelPreferences> | null) {
      if (!this.preferences) {
        this.preferences = preferences;
      } else {
        this.preferences = { ...this.preferences, ...preferences };
      }
    },
    setContext(context: Partial<TravelContext> | null) {
      if (!this.context) {
        this.context = context;
      } else {
        this.context = { ...this.context, ...context };
      }
    },
  },
});
