package main

import (
	"fmt"
	"time"

	"github.com/Mattia-Maiorano/Chronicle/go"
)

func main() {
	chronicle.SetColorMode(true)

	stream := chronicle.NewRollingLogStream(50)

	table := chronicle.NewLiveTable([]chronicle.Column{
		{Header: "Task", MinWidth: 15, Flex: 2},
		{Header: "Status", MinWidth: 10, Align: chronicle.AlignCenter},
		{Header: "Progress", Flex: 3},
	})

	p1 := chronicle.NewProgressBar(100, 0, "Build")
	p2 := chronicle.NewProgressBar(100, 0, "Test")

	table.AddRow("task1", []interface{}{"Frontend", chronicle.NewBadge("RUNNING", chronicle.BadgeRunning), p1})
	table.AddRow("task2", []interface{}{"Backend", chronicle.NewBadge("PENDING", chronicle.BadgeWarn), p2})

	mainLayout := chronicle.NewLayout(chronicle.DirectionVertical)

	headerPanel := chronicle.NewPanel(
		chronicle.NewText("LIVE PIPELINE STATUS", "\x1b[95m", chronicle.AlignCenter),
		"", "", chronicle.BorderRounded,
	)
	mainLayout.Add(headerPanel, chronicle.Fixed(3))

	tablePanel := chronicle.NewPanel(table, "Active Tasks", "", chronicle.BorderDouble)
	mainLayout.Add(tablePanel, chronicle.Flex(1))

	logPanel := chronicle.NewPanel(stream, "Timeline Event Stream", "", chronicle.BorderChronicleTree)
	mainLayout.Add(logPanel, chronicle.Flex(1))

	engine := chronicle.NewLiveEngine(mainLayout, chronicle.ModeAlternateScreen, 10)
	engine.Start()

	stream.Append("INFO: Pipeline started.")

	for i := 1; i <= 50; i++ {
		time.Sleep(100 * time.Millisecond)
		p1.Update(i * 2)

		if i == 25 {
			table.UpdateCell("task1", 1, chronicle.NewBadge("PASS", chronicle.BadgePass))
			table.UpdateCell("task2", 1, chronicle.NewBadge("RUNNING", chronicle.BadgeRunning))
			stream.Append("  +--> DECISION: Frontend Build -> Complete, advancing backend")
		}

		if i > 25 {
			p2.Update((i - 25) * 4)
		}

		if i%10 == 0 {
			stream.Append(fmt.Sprintf("INFO: Processed batch %d", i))
		}
	}

	table.UpdateCell("task2", 1, chronicle.NewBadge("PASS", chronicle.BadgePass))
	stream.Append("  +--> DECISION: Pipeline -> All tasks completed successfully")
	time.Sleep(1 * time.Second)

	engine.Stop()
}
