import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from './useAuth';
import { useReferralConversion } from '@/hooks/useReferralConversion';
import { Eye, EyeOff, User, Building2, Phone, Mail, Lock } from 'lucide-react';

const AuthComponent = () => {
  const { user, loading } = useAuth();
  const { recordConversion } = useReferralConversion();
  const navigate = useNavigate();
  const { toast } = useToast();
  
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: '',
    companyName: '',
    phone: ''
  });

  useEffect(() => {
    if (user && !loading) {
      // Check user role to redirect appropriately
      checkUserRole();
    }
  }, [user, loading]);

  const checkUserRole = async () => {
    if (!user) return;

    try {
      // Check if user is admin
      const { data: adminRole } = await supabase
        .from('user_roles')
        .select('role')
        .eq('user_id', user.id)
        .eq('role', 'admin')
        .single();

      if (adminRole) {
        navigate('/admin', { replace: true });
        return;
      }

      // Check if user is partner
      const { data: partner } = await supabase
        .from('partners')
        .select('id')
        .eq('user_id', user.id)
        .single();

      if (partner) {
        navigate('/partner/dashboard', { replace: true });
      } else {
        navigate('/', { replace: true });
      }
    } catch (error) {
      console.error('Error checking user role:', error);
      navigate('/', { replace: true });
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Get referral data for signup
      const referralData = localStorage.getItem('referral_data');
      let parsedReferralData = null;
      
      if (referralData) {
        try {
          parsedReferralData = JSON.parse(referralData);
          console.log('Using referral data for signup:', parsedReferralData);
        } catch (error) {
          console.error('Error parsing referral data:', error);
        }
      }

      const signUpData = {
        email: formData.email,
        password: formData.password,
        options: {
          data: {
            full_name: formData.fullName,
            company_name: formData.companyName,
            phone: formData.phone,
            referral_source: parsedReferralData?.partner_code || null,
            utm_source: parsedReferralData?.utm_source || null,
            utm_medium: parsedReferralData?.utm_medium || null,
            utm_campaign: parsedReferralData?.utm_campaign || null,
            utm_content: parsedReferralData?.utm_content || null,
            utm_term: parsedReferralData?.utm_term || null,
          }
        }
      };

      console.log('Signing up with data:', signUpData);

      const { data, error } = await supabase.auth.signUp(signUpData);

      if (error) throw error;

      if (data.user) {
        console.log('User registered successfully:', data.user.id);
        console.log('User metadata:', data.user.user_metadata);
        
        // Wait a moment for the profile to be created by the trigger
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Record referral conversion for registration if there's referral data
        if (parsedReferralData?.partner_code) {
          console.log('Recording registration conversion for partner:', parsedReferralData.partner_code);
          try {
            const conversionResult = await recordConversion(data.user.id, 'registration');
            console.log('Registration conversion result:', conversionResult);
          } catch (conversionError) {
            console.error('Failed to record registration conversion:', conversionError);
            // Don't block the registration process if conversion recording fails
          }
        } else {
          console.log('No referral data found, skipping conversion recording');
        }
        
        toast({
          title: "Регистрация успешна!",
          description: "Добро пожаловать! Вы получили 3 дня бесплатного доступа.",
        });
      }
    } catch (error: any) {
      console.error('Signup error:', error);
      toast({
        title: "Ошибка регистрации",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: formData.email,
        password: formData.password,
      });

      if (error) throw error;

      toast({
        title: "Вход выполнен успешно",
        description: "Добро пожаловать обратно!",
      });
    } catch (error: any) {
      console.error('Signin error:', error);
      toast({
        title: "Ошибка входа",
        description: error.message,
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Перенаправление...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold text-center">
            Добро пожаловать
          </CardTitle>
          <CardDescription className="text-center">
            Войдите в свой аккаунт или создайте новый
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="signin" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="signin">Вход</TabsTrigger>
              <TabsTrigger value="signup">Регистрация</TabsTrigger>
            </TabsList>
            
            <TabsContent value="signin">
              <form onSubmit={handleSignIn} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signin-email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signin-email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="your@email.com"
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="signin-password">Пароль</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signin-password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Введите пароль"
                      className="pl-10 pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Вход..." : "Войти"}
                </Button>
              </form>
            </TabsContent>
            
            <TabsContent value="signup">
              <form onSubmit={handleSignUp} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="signup-fullName">Полное имя</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signup-fullName"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleInputChange}
                      placeholder="Ваше полное имя"
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="signup-companyName">Название компании</Label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signup-companyName"
                      name="companyName"
                      value={formData.companyName}
                      onChange={handleInputChange}
                      placeholder="Название вашей компании"
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="signup-phone">Телефон</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signup-phone"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      placeholder="+7 (xxx) xxx-xx-xx"
                      className="pl-10"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="signup-email">Email</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signup-email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      placeholder="your@email.com"
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="signup-password">Пароль</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="signup-password"
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={handleInputChange}
                      placeholder="Создайте пароль"
                      className="pl-10 pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                
                <Button type="submit" className="w-full" disabled={isLoading}>
                  {isLoading ? "Регистрация..." : "Создать аккаунт"}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default AuthComponent;
