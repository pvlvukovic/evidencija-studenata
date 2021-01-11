import React, { useState } from "react";

export default () => {
  const [brojPratilaca, setBrojPratilaca] = useState(0);
  return (
    <button onClick={() => setBrojPratilaca(brojPratilaca + 1)}>Zaprati</button>
  );
};
