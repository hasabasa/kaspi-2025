
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Calendar } from "@/components/ui/calendar";
import { Calendar as CalendarIcon } from "lucide-react";
import { format } from "date-fns";
import { ru } from "date-fns/locale";
import { cn } from "@/lib/utils";

interface DateRangePickerProps {
  dateRange: {
    from?: Date;
    to?: Date;
  };
  onDateRangeChange: (range: { from?: Date; to?: Date }) => void;
}

const DateRangePicker = ({ dateRange, onDateRangeChange }: DateRangePickerProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (date: Date | undefined) => {
    if (!dateRange.from) {
      onDateRangeChange({ from: date, to: undefined });
    } else if (dateRange.from && !dateRange.to && date && date > dateRange.from) {
      onDateRangeChange({ ...dateRange, to: date });
      setIsOpen(false);
    } else {
      onDateRangeChange({ from: date, to: undefined });
    }
  };

  const handleReset = () => {
    onDateRangeChange({});
    setIsOpen(false);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" className="justify-start">
          <CalendarIcon className="mr-2 h-4 w-4" />
          {dateRange.from ? (
            dateRange.to ? (
              <>
                {format(dateRange.from, "d MMM", { locale: ru })} -{" "}
                {format(dateRange.to, "d MMM yyyy", { locale: ru })}
              </>
            ) : (
              format(dateRange.from, "d MMM yyyy", { locale: ru })
            )
          ) : (
            "Выберите период"
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <div className="p-3 border-b">
          <div className="space-y-2">
            <h3 className="font-medium">Выберите диапазон</h3>
            <p className="text-sm text-muted-foreground">
              {dateRange.from
                ? dateRange.to
                  ? "Диапазон выбран"
                  : "Выберите конечную дату"
                : "Выберите начальную дату"}
            </p>
          </div>
        </div>
        <Calendar
          mode="range"
          selected={{
            from: dateRange.from,
            to: dateRange.to,
          }}
          onSelect={(selected: { from?: Date; to?: Date }) => {
            onDateRangeChange(selected || {});
            if (selected?.to) setIsOpen(false);
          }}
          numberOfMonths={2}
          locale={ru}
        />
        <div className="p-3 border-t">
          <Button size="sm" onClick={handleReset} variant="outline" className="w-full">
            Сбросить
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default DateRangePicker;
