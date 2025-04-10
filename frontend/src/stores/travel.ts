import type { TravelContext, TravelPreferences } from "@/types";
import { defineStore } from "pinia";

export const useTravelStore = defineStore("travel", {
  state: () => ({
    preferences: null as TravelPreferences | null,
    context: null as TravelContext | null,
  }),
  actions: {
    setPreferences(preferences: Partial<TravelPreferences> | null) {
      if (preferences) {
        this.preferences = {
          activities: preferences.activities || [],
          accommodation: {
            type: preferences.accommodation?.type || "",
            max_price_per_night: preferences.accommodation?.max_price_per_night || 0,
            amenities: preferences.accommodation?.amenities || [],
          },
          budget: preferences.budget || 0,
          flight: {
            class: preferences.flight?.class || "",
            direct: preferences.flight?.direct || false,
          },
          food_preferences: preferences.food_preferences || [],
        };
      } else {
        this.preferences = null;
      }
    },
    setContext(context: Partial<TravelContext> | null) {
      if (!this.context) {
        if (context) {
          this.context = {
            start_date: context.start_date || "",
            end_date: context.end_date || "",
            origin_city_name: context.origin_city_name || "",
            destination_city_name: context.destination_city_name || "",
            origin_airport_code: context.origin_airport_code || "",
            destination_airport_code: context.destination_airport_code || "",
            num_guests: context.num_guests || 1,
            ...context,
          };
        } else {
          this.context = null;
        }
      } else {
        this.context = { ...this.context, ...context };
      }
    },
    resetTravel() {
      this.preferences = null;
      this.context = null;
    },
  },
});
