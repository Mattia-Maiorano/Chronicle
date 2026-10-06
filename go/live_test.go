package chronicle

import (
	"testing"
)

func TestVisualMeter(t *testing.T) {
	vm := VisualMeter{}
	styled := "\x1b[96mHello World\x1b[0m"
	if vm.StripANSI(styled) != "Hello World" {
		t.Fatalf("expected 'Hello World', got '%s'", vm.StripANSI(styled))
	}
	if vm.Measure(styled) != 11 {
		t.Fatalf("expected length 11, got %d", vm.Measure(styled))
	}
}

func TestFlexSplitterMeasure(t *testing.T) {
	layout := NewLayout(DirectionVertical)
	ctx := RenderContext{Bounds: Size{Width: 100, Height: 24}, ColorMode: true, AsciiMode: false}
	size := layout.Measure(ctx)
	if size.Width != 100 || size.Height != 24 {
		t.Fatalf("unexpected size: %+v", size)
	}
}

func TestLiveTable(t *testing.T) {
	table := NewLiveTable([]Column{
		{Header: "ID", MinWidth: 5},
		{Header: "Status", Flex: 1},
	})
	table.AddRow("row1", []interface{}{"1", "Pending"})
	if len(table.Rows) != 1 {
		t.Fatalf("expected 1 row, got %d", len(table.Rows))
	}

	table.UpdateCell("row1", 1, "Running")
	if table.Rows[0].Cells[1] != "Running" {
		t.Fatalf("expected Running, got %v", table.Rows[0].Cells[1])
	}
}
