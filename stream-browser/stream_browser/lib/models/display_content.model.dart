import 'package:json_annotation/json_annotation.dart';

part 'display_content.model.g.dart';

@JsonSerializable(explicitToJson: true)
class DisplayContent {
  String game;
  String content;

  DisplayContent({
    required this.game,
    required this.content,
  });

  factory DisplayContent.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('DisplayContent: json was null');
    try {
      return _$DisplayContentFromJson(json);
    } catch (e, stack) {
      throw 'DisplayContent.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$DisplayContentToJson(this);
    return json;
  }
}
