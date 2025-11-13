import { Phone, MessageCircle, Mail, MapPin, Clock, Building } from "lucide-react";
import { motion } from "framer-motion";
const Footer = () => {
  return <footer className="bg-white border-t border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          {/* Company Info */}
          <motion.div initial={{
          opacity: 0,
          y: 20
        }} animate={{
          opacity: 1,
          y: 0
        }} transition={{
          duration: 0.6
        }} className="space-y-4">
            <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Вечный ИИ</h3>
            <div className="space-y-2 text-gray-600">
              <div className="flex items-start gap-2">
                <Building className="h-4 w-4 mt-1 text-blue-600" />
                <div>
                  <div className="font-semibold text-gray-900">ТОО "EX-GROUP"</div>
                  <div className="text-sm">БИН: 250440027125</div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Address */}
          <motion.div initial={{
          opacity: 0,
          y: 20
        }} animate={{
          opacity: 1,
          y: 0
        }} transition={{
          duration: 0.6,
          delay: 0.1
        }} className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900">Адрес</h4>
            <div className="flex items-start gap-2 text-gray-600">
              <MapPin className="h-4 w-4 mt-1 text-blue-600" />
              <div className="text-sm leading-relaxed">
                Казахстан, район Нұра,<br />
                улица Мәншүк Мәметова, дом 2,<br />
                кв/офис 190
              </div>
            </div>
          </motion.div>

          {/* Contacts */}
          <motion.div initial={{
          opacity: 0,
          y: 20
        }} animate={{
          opacity: 1,
          y: 0
        }} transition={{
          duration: 0.6,
          delay: 0.2
        }} className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900">Контакты</h4>
            <div className="space-y-3 text-gray-600">
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-green-600" />
                <div>
                  <a href="tel:+77082171960" className="hover:text-gray-900 transition-colors">
                    +7 (708) 217-19-60
                  </a>
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    10:00-18:00
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <MessageCircle className="h-4 w-4 text-green-600" />
                <div>
                  <a href="https://wa.me/77082171960" className="hover:text-gray-900 transition-colors">
                    WhatsApp: +7 (708) 217-19-60
                  </a>
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    10:00-18:00
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-blue-600" />
                <a href="mailto:info@eternal-ai.kz" className="hover:text-gray-900 transition-colors">
                  info@eternal-ai.kz
                </a>
              </div>
            </div>
          </motion.div>

          {/* Links */}
          <motion.div initial={{
          opacity: 0,
          y: 20
        }} animate={{
          opacity: 1,
          y: 0
        }} transition={{
          duration: 0.6,
          delay: 0.3
        }} className="space-y-4">
            <h4 className="text-lg font-semibold text-gray-900">Информация</h4>
            <div className="space-y-2">
              <div>
                <a href="https://eternal-ai.kz" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                  Разработка: eternal-ai.kz
                </a>
              </div>
              <div>
                <a href="https://docs.google.com/document/d/1KiAnPPh4KTIKnMT8H5NrhHtnh_TOjDj-Iwh7gzgmFpc/edit?usp=sharing" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                  Договор оферты
                </a>
              </div>
              <div>
                <a href="https://docs.google.com/document/d/1eENTvZ9aw7y8SPCbW4UMo2u89VtaIBhBiVLknsFbfVU/edit?usp=sharing" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                  Пользовательское соглашение
                </a>
              </div>
              <div>
                <a href="https://docs.google.com/document/d/1ImPXaWTILkUN2ERgB6lLqH7-N1OllC2Xj_fKLjcxDwY/edit?usp=sharing" target="_blank" rel="noopener noreferrer" className="text-gray-600 hover:text-gray-900 transition-colors text-sm">
                  Политика конфиденциальности
                </a>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Bottom Bar */}
        <motion.div initial={{
        opacity: 0
      }} animate={{
        opacity: 1
      }} transition={{
        duration: 0.6,
        delay: 0.4
      }} className="border-t border-gray-200 pt-8 text-center">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-gray-500 text-sm">
              © 2025 ТОО "EX-GROUP". Все права защищены.
            </div>
            <div className="text-gray-500 text-sm">
              Платформа для автоматизации продаж на Kaspi.kz
            </div>
          </div>
        </motion.div>
      </div>
    </footer>;
};
export default Footer;