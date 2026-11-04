import { useState } from "react";

const labels = ["猫", "犬", "鳥"];

export default function App() {
  const [selectedLabel, setSelectedLabel] = useState<string | null>(null);
  const [lastChange, setLastChange] = useState("まだ選択していません");

  function handleLabelChange(nextLabel: string) {
    const previousLabel = selectedLabel ?? "未選択";
    setSelectedLabel(nextLabel);
    setLastChange(`${previousLabel} → ${nextLabel}`);
  }

  return (
    <main>
      <h1>ラベル選択デバッグ</h1>
      <p>画像に付けるラベルを1つ選んでください。正誤判定はありません。</p>
      <img
        src="/sample-cat.svg"
        alt="耳が三角で、ひげのある猫のサンプルイラスト"
        width="360"
        height="240"
      />
      <fieldset>
        <legend>ラベル（1つだけ選択）</legend>
        {labels.map((label) => (
          <label key={label}>
            <input
              type="radio"
              name="image-label"
              value={label}
              checked={selectedLabel === label}
              onChange={() => handleLabelChange(label)}
            />
            {label}
          </label>
        ))}
      </fieldset>
      <section aria-live="polite" aria-label="選択結果">
        <p>選択中のラベル: <strong>{selectedLabel ?? "未選択"}</strong></p>
        <p>直前の選択処理: {lastChange}</p>
      </section>
      <p className="note">
        API・バックエンドには接続しません。選択は保存されず、再読み込みで未選択に戻ります。
      </p>
    </main>
  );
}
