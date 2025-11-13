export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      competitors: {
        Row: {
          created_at: string
          has_delivery: boolean | null
          id: string
          name: string
          price: number
          price_change: number | null
          product_id: string
          rating: number | null
          seller_name: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          has_delivery?: boolean | null
          id?: string
          name: string
          price: number
          price_change?: number | null
          product_id: string
          rating?: number | null
          seller_name?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          has_delivery?: boolean | null
          id?: string
          name?: string
          price?: number
          price_change?: number | null
          product_id?: string
          rating?: number | null
          seller_name?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "competitors_product_id_fkey"
            columns: ["product_id"]
            isOneToOne: false
            referencedRelation: "products"
            referencedColumns: ["id"]
          },
        ]
      }
      kaspi_stores: {
        Row: {
          api_key: string | null
          created_at: string
          id: string
          is_active: boolean
          last_sync: string | null
          merchant_id: string
          name: string
          products_count: number
          updated_at: string
          user_id: string
        }
        Insert: {
          api_key?: string | null
          created_at?: string
          id?: string
          is_active?: boolean
          last_sync?: string | null
          merchant_id: string
          name: string
          products_count?: number
          updated_at?: string
          user_id: string
        }
        Update: {
          api_key?: string | null
          created_at?: string
          id?: string
          is_active?: boolean
          last_sync?: string | null
          merchant_id?: string
          name?: string
          products_count?: number
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      partners: {
        Row: {
          commission_rate: number | null
          company_name: string | null
          contact_email: string | null
          created_at: string | null
          id: string
          instagram_username: string
          is_active: boolean | null
          partner_code: string
          updated_at: string | null
          user_id: string
        }
        Insert: {
          commission_rate?: number | null
          company_name?: string | null
          contact_email?: string | null
          created_at?: string | null
          id?: string
          instagram_username: string
          is_active?: boolean | null
          partner_code: string
          updated_at?: string | null
          user_id: string
        }
        Update: {
          commission_rate?: number | null
          company_name?: string | null
          contact_email?: string | null
          created_at?: string | null
          id?: string
          instagram_username?: string
          is_active?: boolean | null
          partner_code?: string
          updated_at?: string | null
          user_id?: string
        }
        Relationships: []
      }
      products: {
        Row: {
          bot_active: boolean
          category: string | null
          created_at: string
          id: string
          image_url: string | null
          kaspi_product_id: string
          max_profit: number | null
          min_profit: number | null
          name: string
          price: number
          store_id: string
          updated_at: string
        }
        Insert: {
          bot_active?: boolean
          category?: string | null
          created_at?: string
          id?: string
          image_url?: string | null
          kaspi_product_id: string
          max_profit?: number | null
          min_profit?: number | null
          name: string
          price: number
          store_id: string
          updated_at?: string
        }
        Update: {
          bot_active?: boolean
          category?: string | null
          created_at?: string
          id?: string
          image_url?: string | null
          kaspi_product_id?: string
          max_profit?: number | null
          min_profit?: number | null
          name?: string
          price?: number
          store_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "products_store_id_fkey"
            columns: ["store_id"]
            isOneToOne: false
            referencedRelation: "kaspi_stores"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          avatar_url: string | null
          bonus_days: number | null
          company_name: string | null
          created_at: string
          full_name: string | null
          has_paid_subscription: boolean | null
          id: string
          phone: string | null
          phone_verified: boolean | null
          referral_source: string | null
          subscription_end_date: string | null
          updated_at: string
          utm_campaign: string | null
          utm_content: string | null
          utm_medium: string | null
          utm_source: string | null
          utm_term: string | null
        }
        Insert: {
          avatar_url?: string | null
          bonus_days?: number | null
          company_name?: string | null
          created_at?: string
          full_name?: string | null
          has_paid_subscription?: boolean | null
          id: string
          phone?: string | null
          phone_verified?: boolean | null
          referral_source?: string | null
          subscription_end_date?: string | null
          updated_at?: string
          utm_campaign?: string | null
          utm_content?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          utm_term?: string | null
        }
        Update: {
          avatar_url?: string | null
          bonus_days?: number | null
          company_name?: string | null
          created_at?: string
          full_name?: string | null
          has_paid_subscription?: boolean | null
          id?: string
          phone?: string | null
          phone_verified?: boolean | null
          referral_source?: string | null
          subscription_end_date?: string | null
          updated_at?: string
          utm_campaign?: string | null
          utm_content?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          utm_term?: string | null
        }
        Relationships: []
      }
      promo_codes: {
        Row: {
          bonus_days: number | null
          code: string
          created_at: string | null
          expires_at: string | null
          id: string
          is_active: boolean | null
          max_usage: number | null
          partner_id: string | null
          updated_at: string | null
          usage_count: number | null
        }
        Insert: {
          bonus_days?: number | null
          code: string
          created_at?: string | null
          expires_at?: string | null
          id?: string
          is_active?: boolean | null
          max_usage?: number | null
          partner_id?: string | null
          updated_at?: string | null
          usage_count?: number | null
        }
        Update: {
          bonus_days?: number | null
          code?: string
          created_at?: string | null
          expires_at?: string | null
          id?: string
          is_active?: boolean | null
          max_usage?: number | null
          partner_id?: string | null
          updated_at?: string | null
          usage_count?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "promo_codes_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partner_stats"
            referencedColumns: ["partner_id"]
          },
          {
            foreignKeyName: "promo_codes_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partners"
            referencedColumns: ["id"]
          },
        ]
      }
      referral_clicks: {
        Row: {
          created_at: string
          id: string
          page_url: string | null
          partner_id: string
          referrer: string | null
          user_agent: string | null
          utm_campaign: string | null
          utm_content: string | null
          utm_medium: string | null
          utm_source: string | null
          utm_term: string | null
          visitor_ip: unknown | null
        }
        Insert: {
          created_at?: string
          id?: string
          page_url?: string | null
          partner_id: string
          referrer?: string | null
          user_agent?: string | null
          utm_campaign?: string | null
          utm_content?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          utm_term?: string | null
          visitor_ip?: unknown | null
        }
        Update: {
          created_at?: string
          id?: string
          page_url?: string | null
          partner_id?: string
          referrer?: string | null
          user_agent?: string | null
          utm_campaign?: string | null
          utm_content?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          utm_term?: string | null
          visitor_ip?: unknown | null
        }
        Relationships: [
          {
            foreignKeyName: "referral_clicks_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partner_stats"
            referencedColumns: ["partner_id"]
          },
          {
            foreignKeyName: "referral_clicks_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partners"
            referencedColumns: ["id"]
          },
        ]
      }
      referral_conversions: {
        Row: {
          amount: number | null
          commission_earned: number | null
          conversion_type: string | null
          created_at: string | null
          id: string
          notes: string | null
          partner_id: string
          promo_code_id: string | null
          referral_click_id: string | null
          status: string | null
          user_id: string
        }
        Insert: {
          amount?: number | null
          commission_earned?: number | null
          conversion_type?: string | null
          created_at?: string | null
          id?: string
          notes?: string | null
          partner_id: string
          promo_code_id?: string | null
          referral_click_id?: string | null
          status?: string | null
          user_id: string
        }
        Update: {
          amount?: number | null
          commission_earned?: number | null
          conversion_type?: string | null
          created_at?: string | null
          id?: string
          notes?: string | null
          partner_id?: string
          promo_code_id?: string | null
          referral_click_id?: string | null
          status?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "referral_conversions_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partner_stats"
            referencedColumns: ["partner_id"]
          },
          {
            foreignKeyName: "referral_conversions_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partners"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "referral_conversions_promo_code_id_fkey"
            columns: ["promo_code_id"]
            isOneToOne: false
            referencedRelation: "promo_codes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "referral_conversions_referral_click_id_fkey"
            columns: ["referral_click_id"]
            isOneToOne: false
            referencedRelation: "referral_clicks"
            referencedColumns: ["id"]
          },
        ]
      }
      referral_links: {
        Row: {
          created_at: string | null
          id: string
          partner_id: string
          referrer: string | null
          user_agent: string | null
          utm_campaign: string | null
          utm_medium: string | null
          utm_source: string | null
          visitor_ip: string | null
        }
        Insert: {
          created_at?: string | null
          id?: string
          partner_id: string
          referrer?: string | null
          user_agent?: string | null
          utm_campaign?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          visitor_ip?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          partner_id?: string
          referrer?: string | null
          user_agent?: string | null
          utm_campaign?: string | null
          utm_medium?: string | null
          utm_source?: string | null
          visitor_ip?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "referral_links_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partner_stats"
            referencedColumns: ["partner_id"]
          },
          {
            foreignKeyName: "referral_links_partner_id_fkey"
            columns: ["partner_id"]
            isOneToOne: false
            referencedRelation: "partners"
            referencedColumns: ["id"]
          },
        ]
      }
      subscriptions: {
        Row: {
          created_at: string
          expires_at: string
          id: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          expires_at: string
          id?: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          expires_at?: string
          id?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      tasks: {
        Row: {
          created_at: string
          deadline: string | null
          description: string | null
          id: string
          title: string
          user_id: string
        }
        Insert: {
          created_at?: string
          deadline?: string | null
          description?: string | null
          id?: string
          title: string
          user_id: string
        }
        Update: {
          created_at?: string
          deadline?: string | null
          description?: string | null
          id?: string
          title?: string
          user_id?: string
        }
        Relationships: []
      }
      user_roles: {
        Row: {
          created_at: string | null
          id: string
          role: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Insert: {
          created_at?: string | null
          id?: string
          role: Database["public"]["Enums"]["app_role"]
          user_id: string
        }
        Update: {
          created_at?: string | null
          id?: string
          role?: Database["public"]["Enums"]["app_role"]
          user_id?: string
        }
        Relationships: []
      }
      whatsapp_contacts: {
        Row: {
          created_at: string
          id: string
          is_blocked: boolean | null
          last_seen: string | null
          name: string | null
          phone: string
          profile_pic_url: string | null
          session_id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          id?: string
          is_blocked?: boolean | null
          last_seen?: string | null
          name?: string | null
          phone: string
          profile_pic_url?: string | null
          session_id: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          id?: string
          is_blocked?: boolean | null
          last_seen?: string | null
          name?: string | null
          phone?: string
          profile_pic_url?: string | null
          session_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "whatsapp_contacts_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "whatsapp_sessions"
            referencedColumns: ["id"]
          },
        ]
      }
      whatsapp_messages: {
        Row: {
          contact_name: string | null
          contact_phone: string
          created_at: string
          delivery_status: string | null
          id: string
          is_outgoing: boolean
          message_text: string | null
          message_type: string
          session_id: string
          timestamp: string
        }
        Insert: {
          contact_name?: string | null
          contact_phone: string
          created_at?: string
          delivery_status?: string | null
          id?: string
          is_outgoing?: boolean
          message_text?: string | null
          message_type?: string
          session_id: string
          timestamp?: string
        }
        Update: {
          contact_name?: string | null
          contact_phone?: string
          created_at?: string
          delivery_status?: string | null
          id?: string
          is_outgoing?: boolean
          message_text?: string | null
          message_type?: string
          session_id?: string
          timestamp?: string
        }
        Relationships: [
          {
            foreignKeyName: "whatsapp_messages_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "whatsapp_sessions"
            referencedColumns: ["id"]
          },
        ]
      }
      whatsapp_sessions: {
        Row: {
          created_at: string
          id: string
          is_connected: boolean
          last_activity: string | null
          qr_code: string | null
          session_name: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          is_connected?: boolean
          last_activity?: string | null
          qr_code?: string | null
          session_name: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          is_connected?: boolean
          last_activity?: string | null
          qr_code?: string | null
          session_name?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
    }
    Views: {
      partner_stats: {
        Row: {
          instagram_username: string | null
          paid_conversions: number | null
          partner_code: string | null
          partner_id: string | null
          promo_usage: number | null
          registrations: number | null
          total_clicks: number | null
          user_id: string | null
        }
        Relationships: []
      }
    }
    Functions: {
      activate_promo_code: {
        Args: { p_promo_id: string; p_partner_id: string }
        Returns: Json
      }
      apply_promo_code: {
        Args: { p_user_id: string; p_promo_code: string }
        Returns: Json
      }
      create_partner_promo_code: {
        Args: {
          p_partner_id: string
          p_code: string
          p_bonus_days?: number
          p_max_usage?: number
          p_expires_at?: string
        }
        Returns: Json
      }
      delete_user_account: {
        Args: { target_user_id: string }
        Returns: Json
      }
      generate_partner_code: {
        Args: { instagram_name: string }
        Returns: string
      }
      has_role: {
        Args: {
          _user_id: string
          _role: Database["public"]["Enums"]["app_role"]
        }
        Returns: boolean
      }
      is_admin: {
        Args: { user_id?: string }
        Returns: boolean
      }
    }
    Enums: {
      app_role: "admin" | "partner" | "user"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof Database },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
  ? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      app_role: ["admin", "partner", "user"],
    },
  },
} as const
