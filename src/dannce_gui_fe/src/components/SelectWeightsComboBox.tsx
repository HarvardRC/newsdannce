'use client';

import { forwardRef, useState } from 'react';
import { Check, ChevronsUpDown } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

import { ControllerRenderProps } from 'react-hook-form';

type CustomProps = {
  options: {
    name: string;
    id: number;
  }[];
  mode: 'COM' | 'DANNCE';
} & ControllerRenderProps;

const SelectWeightsComboBox = forwardRef<any, CustomProps>(
  ({ options: optionsUnsafe, mode, ...field }, ref) => {
    //  Ref is unused
    const [open, setOpen] = useState(false);
    const value = field.value as number | null;
    const setValue = (newValue: number | null) => {
      field.onChange(newValue);
    };
    const valueAsString = value ? value.toString() : null;

    // cmdk requires value to be a string. Map options array to a format that cmdk will like
    const optionsSafe = optionsUnsafe.map((x) => ({
      label: x.name,
      value: x.id.toString(),
    }));

    return (
      <div>
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              role="combobox"
              aria-expanded={open}
              className="w-[400px] justify-between"
            >
              {valueAsString
                ? optionsSafe.find(
                    (optionsSafe) => optionsSafe.value === valueAsString
                  )?.label
                : 'Select model...'}
              <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-[400px] p-0">
            <Command
              // Case-insensitive search which includes the label ("Model name") and value ("Model Id" as str)
              filter={(value, search, keywords) => {
                const extendValue = (
                  value +
                  ' ' +
                  keywords!.join(' ')
                ).toLowerCase();
                if (extendValue.includes(search.toLowerCase())) return 1;
                return 0;
              }}
            >
              <CommandInput placeholder={`Select ${mode} model`} />
              <CommandList>
                <CommandEmpty>No trained {mode} model found.</CommandEmpty>
                <CommandGroup>
                  {optionsSafe.map((optionsSafe) => (
                    <CommandItem
                      key={optionsSafe.value}
                      value={optionsSafe.value}
                      keywords={[optionsSafe.label]}
                      onSelect={(currentValue) => {
                        setValue(
                          currentValue === valueAsString
                            ? null
                            : parseInt(currentValue)
                        );
                        setOpen(false);
                      }}
                    >
                      <Check
                        className={cn(
                          'mr-2 h-4 w-4',
                          valueAsString === optionsSafe.value
                            ? 'opacity-100'
                            : 'opacity-0'
                        )}
                      />
                      [{optionsSafe.value}]: {optionsSafe.label}
                    </CommandItem>
                  ))}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>
    );
  }
);

export default SelectWeightsComboBox;
