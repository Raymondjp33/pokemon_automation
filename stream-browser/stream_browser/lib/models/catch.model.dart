import 'package:json_annotation/json_annotation.dart';

part 'catch.model.g.dart';

@JsonSerializable(explicitToJson: true)
class CatchModel {
  int? encounters;
  @JsonKey(name: 'switch')
  int switchUsed;
  @JsonKey(name: 'encounter_method')
  String? encounterMethod;
  @JsonKey(name: 'catch_name')
  String? name;
  @JsonKey(name: 'caught_timestamp')
  num? caughtTimestamp;

  CatchModel({
    this.encounters,
    this.caughtTimestamp,
    this.encounterMethod,
    this.name,
    this.switchUsed = 1,
  });

  factory CatchModel.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('CatchModel: json was null');
    try {
      return _$CatchModelFromJson(json);
    } catch (e, stack) {
      throw 'CatchModel.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$CatchModelToJson(this);
    return json;
  }
}
