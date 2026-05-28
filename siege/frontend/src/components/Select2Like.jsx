import Select from 'react-select'

export default function Select2Like({ className, ...props }) {
  return (
    <Select
      className={className}
      classNamePrefix="rs"
      menuPortalTarget={document.body}
      styles={{
        menuPortal: base => ({ ...base, zIndex: 2000 }),
      }}
      {...props}
    />
  )
}

