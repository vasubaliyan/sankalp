export function sanitizeInput(value) {
    console.log("sanitized")
  return value.replace(/[<>]/g, ""); // basic removal of HTML tags
}